from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager

from api.company import router as company_router
from core.config import settings
from core.db.models import Base
from core.db.base import engine
# from services.company_service import check_premium_expiry

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 데이터베이스 초기화
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 정기적으로 프리미엄 만료 체크하는 태스크 시작
    # task = asyncio.create_task(check_premium_expiry())
    
    yield
    
    # 종료 시 태스크 취소
    # task.cancel()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(company_router, prefix=settings.API_V1_STR) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)

# uvicorn main:app --reload --port 8001