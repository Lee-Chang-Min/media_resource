from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from core.db.models import Company
from core.db.schemas import CompanyCreate, CompanyUpdate


# 회사 이름으로 조회 (중복 체크)
async def get_company(db: AsyncSession, name: str) -> Optional[Company]:
    result = await db.execute(select(Company).where(Company.name == name))

    return result.scalar_one_or_none()

# 회사 생성
async def create_company(db: AsyncSession, company_in: CompanyCreate) -> Company:

    premium_expiry_date = None
    if company_in.premium and company_in.premium_expiry_date:
        # 현재 시간 가져오기
        now = datetime.now()
        
        # premium_expiry_date 값에 따라 개월 수 추가
        months_to_add = 0
        if company_in.premium_expiry_date == 1:
            months_to_add = 1
        elif company_in.premium_expiry_date == 3:
            months_to_add = 3
        elif company_in.premium_expiry_date == 12:
            months_to_add = 12
            
        # 현재 시간에 개월 수 추가
        premium_expiry_date = now + relativedelta(months=months_to_add)
        print(premium_expiry_date)

    db_company = Company(
        name=company_in.name,
        premium=company_in.premium,
        premium_expiry_date=premium_expiry_date
    )
    
    db.add(db_company)
    await db.commit()
    await db.refresh(db_company)

    return db_company

