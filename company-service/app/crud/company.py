from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List

from app.models import Company
from app.schemas import CompanyCreate, CompanyUpdate

async def get_company_by_name(db: AsyncSession, name: str) -> Optional[Company]:
    result = await db.execute(select(Company).where(Company.name == name))
    return result.scalar_one_or_none()

async def create_company(db: AsyncSession, company_in: CompanyCreate) -> Company:
    db_company = Company(
        name=company_in.name,
        is_premium=company_in.is_premium,
        premium_expiry_date=company_in.premium_expiry_date
    )
    
    db.add(db_company)
    await db.commit()
    await db.refresh(db_company)
    return db_company

# 다른 CRUD 함수 추가 (조회, 수정, 삭제 등) 