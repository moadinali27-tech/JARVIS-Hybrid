from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.sql import func
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    language = Column(String, default="ar")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String, default="محادثة جديدة")
    language = Column(String, default="ar")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    message_type = Column(String)  # "user", "assistant"
    content = Column(Text)
    language = Column(String, default="ar")
    sentiment = Column(String, nullable=True)  # "positive", "negative", "neutral"
    created_at = Column(DateTime, default=datetime.utcnow)

class ContextMemory(Base):
    __tablename__ = "context_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    key = Column(String, index=True)
    value = Column(Text)
    importance = Column(Float, default=0.5)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SecurityLog(Base):
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    event_type = Column(String)  # "login", "logout", "alert", etc.
    description = Column(Text)
    ip_address = Column(String, nullable=True)
    camera_detected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String)
    description = Column(Text)
    status = Column(String)  # "success", "error", "warning"
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
