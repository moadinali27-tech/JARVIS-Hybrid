import google.generativeai as genai
from config import settings
from typing import Optional
import asyncio

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.AI_MODEL)
        self.conversation_history = {}
    
    async def get_response(self, 
                          message: str, 
                          conversation_id: Optional[int] = None,
                          language: str = "ar",
                          context: Optional[str] = None) -> str:
        """
        احصل على رد من Gemini API مع دعم السياق
        """
        try:
            # بناء النص مع السياق
            full_prompt = self._build_prompt(message, language, context)
            
            # محاولة الحصول على رد من الـ API
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(full_prompt)
            )
            
            # حفظ السياق للمحادثة
            if conversation_id:
                if conversation_id not in self.conversation_history:
                    self.conversation_history[conversation_id] = []
                self.conversation_history[conversation_id].append({
                    "role": "user",
                    "content": message
                })
                self.conversation_history[conversation_id].append({
                    "role": "assistant",
                    "content": response.text
                })
            
            return response.text
        
        except Exception as e:
            # في حالة الخطأ، استخدم نموذج محلي
            return await self.get_offline_response(message, language)
    
    async def get_offline_response(self, message: str, language: str = "ar") -> str:
        """
        احصل على رد من نموذج محلي بدون إنترنت
        """
        try:
            import ollama
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ollama.generate(
                    model=settings.LOCAL_MODEL,
                    prompt=message,
                    stream=False
                )
            )
            
            return response.get("response", "عذراً، لم أتمكن من معالجة الطلب")
        
        except Exception as e:
            # رسالة افتراضية إذا فشل كل شيء
            return self._get_fallback_response(language)
    
    def _build_prompt(self, message: str, language: str, context: Optional[str]) -> str:
        """
        بناء prompt مخصص حسب اللغة والسياق
        """
        language_prefix = {
            "ar": "أنت جارفيس، مساعد ذكاء اصطناعي متقدم وودود. رد بشكل طبيعي وودي.",
            "en": "You are JARVIS, an advanced and friendly AI assistant. Respond naturally and warmly.",
            "fr-MA": "Vous êtes JARVIS, un assistant IA avancé et amical. Répondez naturellement et chaleureusement."
        }
        
        prefix = language_prefix.get(language, language_prefix["ar"])
        
        if context:
            return f"{prefix}\n\nسياق المحادثة:\n{context}\n\nالسؤال: {message}"
        else:
            return f"{prefix}\n\nالسؤال: {message}"
    
    def _get_fallback_response(self, language: str) -> str:
        """
        رد افتراضي إذا فشل الاتصال
        """
        responses = {
            "ar": "أعتذر، يبدو أنني في وضع عدم اتصال حالياً. سأحاول مجدداً قريباً.",
            "en": "I apologize, it seems I'm offline right now. I'll try again soon.",
            "fr-MA": "Je m'excuse, il semble que je sois hors ligne pour le moment. Je vais réessayer bientôt."
        }
        return responses.get(language, responses["ar"])
    
    def get_context(self, conversation_id: int) -> str:
        """احصل على سياق المحادثة السابقة"""
        if conversation_id in self.conversation_history:
            history = self.conversation_history[conversation_id]
            context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in history[-6:]  # آخر 3 رسائل فقط
            ])
            return context
        return ""

ai_service = AIService()
