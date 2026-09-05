from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
from datetime import datetime

from config import settings
from database import init_db, get_db
from schemas import AIRequest, AIResponse, VoiceRequest, UserCreate, LoginRequest, TokenResponse
from services.ai_service import ai_service
from services.voice_service import voice_service
from services.security_service import security_service

# تهيئة التطبيق
app = FastAPI(
    title="JARVIS-Hybrid API",
    description="نظام الذكاء الاصطناعي المنزلي المتكامل",
    version="1.0.0"
)

# إضافة CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# متغيرات عام
connected_clients = {}

# =============== Startup & Shutdown ===============
@app.on_event("startup")
async def startup_event():
    """تهيئة النظام عند البدء"""
    print("🤖 جارفيس يبدأ التشغيل...")
    
    # تهيئة قاعدة البيانات
    init_db()
    print("✅ قاعدة البيانات جاهزة")
    
    # تهيئة الكاميرا
    camera_ok = await security_service.initialize_camera()
    if camera_ok:
        print("✅ الكاميرا جاهزة")
        await security_service.start_motion_detection()
    else:
        print("⚠️ الكاميرا غير متاحة")
    
    print("✅ جارفيس جاهز للعمل!")

@app.on_event("shutdown")
async def shutdown_event():
    """تنظيف الموارد عند الإغلاق"""
    print("🛑 إيقاف جارفيس...")
    await security_service.stop_recording()
    await security_service.release_camera()
    print("✅ تم الإغلاق بنجاح")

# =============== Routes ===============

@app.get("/health")
async def health_check():
    """التحقق من حالة النظام"""
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "ai_mode": "online",
        "camera": security_service.get_status()
    }

@app.post("/ai/chat", response_model=AIResponse)
async def chat(request: AIRequest):
    """معالجة طلب الدردشة"""
    try:
        # الحصول على السياق
        context = ai_service.get_context(request.conversation_id) if request.conversation_id else None
        
        # الحصول على رد من الـ AI
        response = await ai_service.get_response(
            message=request.message,
            conversation_id=request.conversation_id,
            language=request.language,
            context=context
        )
        
        # تحويل النص إلى صوت
        audio_data = await voice_service.text_to_speech(response, request.language)
        
        return AIResponse(
            response=response,
            conversation_id=request.conversation_id or 0,
            message_id=1,
            language=request.language,
            audio_url="/audio/last"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/transcribe")
async def transcribe_voice(request: VoiceRequest):
    """تحويل الصوت إلى نص"""
    try:
        # فك تشفير البيانات
        import base64
        audio_bytes = base64.b64decode(request.audio_data)
        
        # تحويل الصوت إلى نص
        text, confidence = await voice_service.speech_to_text(audio_bytes, request.language)
        
        # كشف اللغة
        detected_language = voice_service.detect_language(text)
        
        return {
            "text": text,
            "language": detected_language,
            "confidence": confidence
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/voice/synthesize")
async def synthesize_voice(text: str, language: str = "ar"):
    """تحويل النص إلى صوت"""
    try:
        audio_bytes = await voice_service.text_to_speech(text, language)
        
        return {
            "audio": audio_bytes.hex(),
            "language": language,
            "length": len(audio_bytes)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/security/camera/frame")
async def get_camera_frame():
    """الحصول على صورة من الكاميرا"""
    try:
        frame = await security_service.capture_frame()
        
        if frame is None:
            raise HTTPException(status_code=503, detail="الكاميرا غير متاحة")
        
        import base64
        return {
            "frame": base64.b64encode(frame).decode(),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security/status")
async def get_security_status():
    """الحصول على حالة الأمان"""
    return security_service.get_status()

@app.post("/security/motion-detection/start")
async def start_motion_detection():
    """بدء كشف الحركة"""
    try:
        await security_service.start_motion_detection()
        return {"status": "motion detection started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/security/motion-detection/stop")
async def stop_motion_detection():
    """إيقاف كشف الحركة"""
    try:
        await security_service.stop_recording()
        return {"status": "motion detection stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============== WebSocket ===============
@app.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: int):
    """اتصال WebSocket للدردشة المباشرة"""
    await websocket.accept()
    connected_clients[user_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # معالجة الرسالة
            response = await ai_service.get_response(
                message=data.get("message"),
                language=data.get("language", "ar")
            )
            
            # إرسال الرد
            await websocket.send_json({
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
    
    except WebSocketDisconnect:
        del connected_clients[user_id]
    
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        del connected_clients[user_id]

# =============== Error Handlers ===============
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG
    )
