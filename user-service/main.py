from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.db.models import Base
from core.db.base import engine

# from core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from api.user import router as user_router

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(user_router, prefix=settings.API_V1_STR) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)

# uvicorn main:app --reload --port 8000