from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List

from core.db.models import Company
from core.db.schemas import CompanyCreate, CompanyUpdate


# 회사 이름으로 조회
async def get_company(db: AsyncSession, name: str) -> Optional[Company]:
    result = await db.execute(select(Company).where(Company.name == name))

    return result.scalar_one_or_none()

# 회사 생성
async def create_company(db: AsyncSession, company_in: CompanyCreate) -> Company:
    db_company = Company(
        name=company_in.name,
        premium=company_in.premium,
        premium_expiry_date=company_in.premium_expiry_date
    )
    
    db.add(db_company)
    await db.commit()
    await db.refresh(db_company)
    return db_company

