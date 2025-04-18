from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.api.v1 import api_router
from app.core.config import settings
from app.models import Base
from app.core.db import engine
from app.services.premium_service import check_premium_expiry

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup():
    # 데이터베이스 초기화
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 정기적으로 프리미엄 만료 체크하는 태스크 시작
    asyncio.create_task(check_premium_expiry()) 