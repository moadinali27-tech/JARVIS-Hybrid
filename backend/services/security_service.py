import cv2
import asyncio
from datetime import datetime
from typing import Dict, Optional
import threading

class SecurityService:
    def __init__(self):
        self.camera = None
        self.is_recording = False
        self.motion_detected = False
        self.alert_callback = None
        self.frame_count = 0
        self.motion_threshold = 5000  # threshold for motion detection
    
    async def initialize_camera(self) -> bool:
        """
        تهيئة الكاميرا
        """
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self._init_camera
            )
            return success
        except Exception as e:
            print(f"خطأ في تهيئة الكاميرا: {e}")
            return False
    
    def _init_camera(self) -> bool:
        """تهيئة الكاميرا بشكل متزامن"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                return False
            
            # ضبط خصائص الكاميرا
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            return True
        except:
            return False
    
    async def start_motion_detection(self, callback=None):
        """
        بدء كشف الحركة
        """
        self.alert_callback = callback
        self.is_recording = True
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._motion_detection_loop
        )
    
    def _motion_detection_loop(self):
        """حلقة كشف الحركة"""
        prev_frame = None
        
        while self.is_recording:
            try:
                if not self.camera or not self.camera.isOpened():
                    continue
                
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                # تحويل الإطار إلى رمادي للمعالجة
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                
                if prev_frame is not None:
                    # حساب الفرق بين الإطارات
                    frame_diff = cv2.absdiff(prev_frame, gray)
                    _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
                    
                    # حساب عدد البكسلات المختلفة
                    motion_pixels = cv2.countNonZero(thresh)
                    
                    # إذا تجاوزت الحركة الحد
                    if motion_pixels > self.motion_threshold:
                        if not self.motion_detected:
                            self.motion_detected = True
                            self._trigger_alert("motion_detected", {
                                "motion_pixels": motion_pixels,
                                "timestamp": datetime.now().isoformat()
                            })
                    else:
                        self.motion_detected = False
                
                prev_frame = gray
                self.frame_count += 1
                
                # استراحة قصيرة
                asyncio.sleep(0.01)
            
            except Exception as e:
                print(f"خطأ في كشف الحركة: {e}")
                continue
    
    def _trigger_alert(self, alert_type: str, data: Dict):
        """تشغيل التنبيه"""
        if self.alert_callback:
            asyncio.create_task(self.alert_callback(alert_type, data))
    
    async def capture_frame(self) -> Optional[bytes]:
        """
        التقاط صورة من الكاميرا
        """
        try:
            if not self.camera or not self.camera.isOpened():
                return None
            
            loop = asyncio.get_event_loop()
            frame = await loop.run_in_executor(
                None,
                self._capture_frame
            )
            
            return frame
        except Exception as e:
            print(f"خطأ في التقاط الصورة: {e}")
            return None
    
    def _capture_frame(self) -> Optional[bytes]:
        """التقاط الإطار بشكل متزامن"""
        try:
            ret, frame = self.camera.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                return buffer.tobytes()
            return None
        except:
            return None
    
    async def stop_recording(self):
        """
        إيقاف التسجيل
        """
        self.is_recording = False
    
    async def release_camera(self):
        """
        تحرير الكاميرا
        """
        self.is_recording = False
        if self.camera:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.camera.release()
            )
    
    def get_status(self) -> Dict:
        """
        الحصول على حالة النظام الأمني
        """
        return {
            "camera_active": self.camera is not None and self.camera.isOpened(),
            "motion_detection": self.is_recording,
            "motion_detected": self.motion_detected,
            "frames_processed": self.frame_count
        }

security_service = SecurityService()
