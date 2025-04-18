from pydantic import BaseSettings, PostgresDsn, validator
from typing import Optional, Dict, Any
import secrets
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Company Service"
    API_V1_STR: str = "/api/v1"
    
    # 데이터베이스 설정
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "company"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[PostgresDsn] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # 인증 서비스 URL
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    
    # 보안 설정
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # 프리미엄 설정
    DEFAULT_PREMIUM_DAYS: int = 30
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 