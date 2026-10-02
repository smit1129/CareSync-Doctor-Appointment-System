import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Doctor Appointment Management System"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Supabase / PostgreSQL or local SQLite fallback for seamless execution
    DATABASE_URL: str = os.getenv("DATABASE_URL", os.getenv("SUPABASE_DB_URL", "sqlite:///./doctor_appointments.db"))
    
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

    @property
    def parsed_cors_origins(self) -> List[str]:
        origins = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL.strip())
        return origins

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "allow"
    }

settings = Settings()

if not settings.SECRET_KEY or settings.SECRET_KEY == "generate-a-strong-random-secret-here":
    raise RuntimeError("⛔ SECRET_KEY is not set. Please set a strong SECRET_KEY in your environment variables or .env file.")
