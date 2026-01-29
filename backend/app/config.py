import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Visa Document Processing System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    
    # Server
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 3000
    
    # Database
    DATABASE_URL: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "visa_processing_db"
    DB_USER: str
    DB_PASSWORD: str
    
    # Gemini AI
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_EXTENSIONS: str = "pdf,jpg,jpeg,png"
    UPLOAD_FOLDER: str = "./uploads"
    GENERATED_FOLDER: str = "./generated"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Visa Configuration - Iceland Tourist Visa
    SUPPORTED_COUNTRIES: list = ["Iceland"]
    SUPPORTED_VISA_TYPES: list = ["Tourist"]
    
    @property
    def allowed_extensions_list(self) -> list:
        """Get allowed file extensions as list"""
        return self.ALLOWED_FILE_EXTENSIONS.split(',')
    
    @property
    def cors_origins_list(self) -> list:
        """Get CORS origins as list"""
        return self.CORS_ORIGINS.split(',')
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create settings instance
settings = get_settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.GENERATED_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
