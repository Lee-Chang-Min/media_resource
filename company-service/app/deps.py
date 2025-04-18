from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generator

from app.core.db import async_session

async def get_db() -> Generator:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# 현재 사용자 및 관리자 접근 확인 함수 추가
async def get_current_user():
    # JWT 토큰 검증 및 현재 사용자 반환 로직
    pass

async def get_current_admin_user():
    # 관리자 권한 확인 로직
    pass 