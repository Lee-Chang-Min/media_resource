from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import asyncio

from app.models import Company
from app.core.db import async_session

async def check_premium_expiry():
    while True:
        async with async_session() as session:
            # 만료된 프리미엄 플랜 찾기
            now = datetime.utcnow()
            result = await session.execute(
                select(Company).where(
                    Company.is_premium == True,
                    Company.premium_expiry_date <= now
                )
            )
            
            expired_companies = result.scalars().all()
            
            # 만료된 플랜 업데이트
            for company in expired_companies:
                company.is_premium = False
                session.add(company)
            
            await session.commit()
        
        # 하루에 한 번 체크
        await asyncio.sleep(86400) 