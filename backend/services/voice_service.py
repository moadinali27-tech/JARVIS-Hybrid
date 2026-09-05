import speech_recognition as sr
import pyttsx3
from typing import Tuple, Optional
import asyncio
import base64
import io

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        
        # إعدادات محرك الصوت
        self.engine.setProperty('rate', 150)  # السرعة
        self.engine.setProperty('volume', 1.0)  # مستوى الصوت
        
        # اختيار الصوت العربي إذا كان متاحاً
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'arabic' in voice.name.lower() or 'ar' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    async def speech_to_text(self, 
                           audio_data: Optional[bytes] = None,
                           language: str = "ar") -> Tuple[str, float]:
        """
        تحويل الصوت إلى نص
        """
        try:
            language_codes = {
                "ar": "ar-SA",
                "en": "en-US",
                "fr-MA": "fr-FR"
            }
            
            lang_code = language_codes.get(language, "ar-SA")
            
            if audio_data:
                # معالجة البيانات المرسلة
                audio = sr.AudioData(audio_data, 16000, 2)
            else:
                # التقاط الصوت من الميكروفون
                with sr.Microphone() as source:
                    try:
                        audio = self.recognizer.listen(source, timeout=5)
                    except sr.RequestError:
                        return "لم أتمكن من التقاط الصوت", 0.0
            
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None,
                lambda: self.recognizer.recognize_google(audio, language=lang_code)
            )
            
            # حساب مستوى الثقة (افتراضي)
            confidence = 0.85
            
            return text, confidence
        
        except sr.UnknownValueError:
            return "لم أفهم ما قلت بوضوح", 0.0
        except sr.RequestError:
            return "خطأ في خدمة التعرف على الكلام", 0.0
        except Exception as e:
            return f"خطأ: {str(e)}", 0.0
    
    async def text_to_speech(self, 
                            text: str, 
                            language: str = "ar",
                            speed: float = 1.0) -> bytes:
        """
        تحويل النص إلى صوت
        """
        try:
            # تعديل السرعة
            self.engine.setProperty('rate', int(150 * speed))
            
            # حفظ الصوت في ملف مؤقت
            loop = asyncio.get_event_loop()
            
            # إنشاء ملف مؤقت
            output = io.BytesIO()
            self.engine.save_to_file(text, 'temp_audio.mp3')
            
            await loop.run_in_executor(None, lambda: self.engine.runAndWait())
            
            # قراءة الملف وتحويله إلى bytes
            with open('temp_audio.mp3', 'rb') as f:
                audio_bytes = f.read()
            
            return audio_bytes
        
        except Exception as e:
            print(f"خطأ في تحويل النص إلى صوت: {e}")
            return b""
    
    def detect_language(self, text: str) -> str:
        """
        كشف اللغة من النص
        """
        try:
            from langdetect import detect
            
            detected = detect(text)
            
            language_map = {
                "ar": "ar",
                "en": "en",
                "fr": "fr-MA"
            }
            
            return language_map.get(detected, "ar")
        
        except:
            # إذا فشل الكشف، افترض العربية
            return "ar"
    
    def set_voice_properties(self, rate: int = 150, volume: float = 1.0):
        """
        ضبط خصائص الصوت
        """
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
    
    async def speak(self, text: str, language: str = "ar"):
        """
        تشغيل الصوت مباشرة
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.engine.say(text)
            )
            await loop.run_in_executor(
                None,
                lambda: self.engine.runAndWait()
            )
        except Exception as e:
            print(f"خطأ في تشغيل الصوت: {e}")

voice_service = VoiceService()
