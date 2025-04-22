from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from core.db.models import Company
from core.db.schemas import CompanyCreate, CompanyUpdate


# 회사 이름으로 조회 
async def get_company(db: AsyncSession, name: str) -> Optional[Company]:
    result = await db.execute(select(Company).where(Company.name == name))

    return result.scalar_one_or_none()

# 회사 플랜 조회
async def get_company_plan_db(db: AsyncSession, company_id: int) -> Optional[Company]:
    result = await db.execute(select(Company).where(Company.id == company_id))

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
        name=company_in.company_name,
        premium=company_in.premium,
        premium_expiry_date=premium_expiry_date
    )
    
    db.add(db_company)
    await db.commit()
    await db.refresh(db_company)

    return db_company

# 회사 플랜 수정
async def update_company_db(db: AsyncSession, company_id: int, company_in: CompanyUpdate) -> Company:
    company = await db.execute(select(Company).where(Company.id == company_id))
    db_company = company.scalar_one_or_none()

    # 플랜 만료일 설정 Utile 함수로 빼기
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
        # 무료에서 유료로 전환되거나 기존 만료일이 없는 경우 현재 날짜 기준으로 설정
        if not db_company.premium or db_company.premium_expiry_date is None:
            premium_expiry_date = now + relativedelta(months=months_to_add)
        else:
            premium_expiry_date = db_company.premium_expiry_date + relativedelta(months=months_to_add)


    if db_company:
        db_company.premium = company_in.premium
        db_company.premium_expiry_date = premium_expiry_date
        await db.commit()
        await db.refresh(db_company)

    return db_company

# 회사 삭제
async def delete_company(db: AsyncSession, company_id: int) -> None:
    company = await db.execute(select(Company).where(Company.id == company_id))
    db_company = company.scalar_one_or_none()
    if db_company:
        await db.delete(db_company)
        await db.commit()