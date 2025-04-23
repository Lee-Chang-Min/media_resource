from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Video Service"
    API_V1_STR: str = "/v1"
    PORT: int = 8002

    # 데이터베이스 설정
    POSTGRES_SERVER: str = "postgres"
    # POSTGRES_SERVER: str = "localhost"
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

    # COMPANY_SERVICE_URL: str = "http://company-service:8001"
    COMPANY_SERVICE_URL: str = "http://company-service:8001"
    USER_SERVICE_URL: str = "http://user-service:8000"

    
    JWT_SECRET_KEY: str = "lcmlcm123456789"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_EXPIRE_DAYS: int = 28

settings = Settings()