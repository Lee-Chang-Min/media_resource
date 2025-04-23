from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.db.models import Base
from core.db.base import engine
from api.video import router as video_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 실행
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield 

app = FastAPI(title="Video Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API 라우터 포함
app.include_router(video_router, prefix=settings.API_V1_STR) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)

# uvicorn main:app --reload --port 8002