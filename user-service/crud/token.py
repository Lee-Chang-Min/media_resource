from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models import RefreshToken


# DB RefreshToken 저장
async def create_refresh_token(
    db: AsyncSession,
    token: str,
    user_id: int,
    expires_delta: timedelta
) -> RefreshToken:
    try:
        new_refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=datetime.now(timezone.utc) + expires_delta
        )
        
        db.add(new_refresh_token)
        await db.commit()
        return new_refresh_token
    except Exception as e:
        await db.rollback()
        raise e

# DB에 저장된 토큰 객체 조회
async def get_by_token(db: AsyncSession, token: str) -> RefreshToken | None:
    try:
        result = await db.execute(select(RefreshToken).where(RefreshToken.token == token))
        return result.scalar_one_or_none()
    except Exception as e:
        raise e

# 토큰 생성


