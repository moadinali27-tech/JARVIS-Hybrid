import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Settings:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///jarvis.db")
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"
    
    # Server
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
    
    # CORS
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    ALGORITHM = "HS256"
    
    # Audio
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    
    # AI
    AI_MODEL = "gemini-pro"
    LOCAL_MODEL = "mistral"  # For offline mode
    
    # Languages
    SUPPORTED_LANGUAGES = ["ar", "en", "fr-MA"]
    DEFAULT_LANGUAGE = "ar"
    
    # Security
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_ATTEMPT_TIMEOUT = timedelta(minutes=15)

settings = Settings()
