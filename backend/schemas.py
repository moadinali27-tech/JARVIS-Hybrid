from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    language: str = "ar"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Conversation Schemas
class ConversationCreate(BaseModel):
    title: Optional[str] = None
    language: str = "ar"

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    language: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Message Schemas
class MessageCreate(BaseModel):
    conversation_id: int
    content: str
    message_type: str = "user"
    language: str = "ar"

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    user_id: int
    message_type: str
    content: str
    language: str
    sentiment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Context Memory Schemas
class ContextMemoryCreate(BaseModel):
    key: str
    value: str
    importance: float = 0.5

class ContextMemoryResponse(BaseModel):
    id: int
    user_id: int
    key: str
    value: str
    importance: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# AI Request/Response
class AIRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    language: str = "ar"

class AIResponse(BaseModel):
    response: str
    conversation_id: int
    message_id: int
    language: str
    audio_url: Optional[str] = None

# Voice Request/Response
class VoiceRequest(BaseModel):
    audio_data: str  # Base64 encoded
    language: str = "ar"

class VoiceResponse(BaseModel):
    text: str
    language: str
    confidence: float

# Security
class SecurityAlert(BaseModel):
    event_type: str
    description: str
    camera_detected: bool
    timestamp: datetime

class SecurityLogResponse(BaseModel):
    id: int
    event_type: str
    description: str
    camera_detected: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# System Status
class SystemStatus(BaseModel):
    status: str  # "online", "offline"
    ai_mode: str  # "online", "local"
    memory_usage: float
    cpu_usage: float
    uptime: float
    connected_devices: int
    last_activity: datetime
    camera_status: str  # "active", "inactive", "recording"

# Login Request
class LoginRequest(BaseModel):
    username: str
    password: str

# Token Response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
