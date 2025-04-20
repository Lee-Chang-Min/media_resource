from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Company Service"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8001

    # 데이터베이스 설정
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "lumanlab"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info):
        if isinstance(v, str):
            return v
        values = info.data
        dsn = (
            f"postgresql+asyncpg://{values['POSTGRES_USER']}:{values['POSTGRES_PASSWORD']}"
            f"@{values['POSTGRES_SERVER']}:{values['POSTGRES_PORT']}/{values['POSTGRES_DB']}"
        )
        return dsn  
    
    # 인증 서비스 URL
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    
    # 플랜 기간 설정
    DEFAULT_PREMIUM_DAYS: int = 30
    

settings = Settings()