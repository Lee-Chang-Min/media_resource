from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update
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
async def get_by_refresh_token(db: AsyncSession, user_id: int) -> RefreshToken | None:
    try:
        result = await db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .order_by(RefreshToken.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        raise e

# refresh token 무효화
async def token_revoke(db: AsyncSession, refresh_token: str):
    try:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.token == refresh_token)
            .values(revoked_at=datetime.now(timezone.utc))
        )   
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e

