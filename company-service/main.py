import asyncio
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.company import router as company_router
from core.config import settings
from core.db.models import Base
from core.db.base import engine
from sqlalchemy.ext.asyncio import AsyncSession
from services.company_service import check_plan_expiry
from core.db.base import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 데이터베이스 초기화
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 2) 백그라운드 태스크 시작 (세션은 태스크 내부에서 열음)
    task = asyncio.create_task(check_plan_expiry())

    yield  # 앱이 살아있는 동안

    # 3) 서버 종료 시 태스크 안전하게 취소
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("플랜 만료 체크 태스크 취소")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(company_router, prefix=settings.API_V1_STR) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)

# uvicorn main:app --reload --port 8001