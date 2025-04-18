from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud import company as company_crud
from app.schemas import Company, CompanyCreate, CompanyUpdate
from app.deps import get_db, get_current_user, get_current_admin_user
from app.services.admin_service import create_admin_user

router = APIRouter()

@router.post("/", response_model=Company)
async def create_company(
    company_in: CompanyCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # 회사 이름 중복 체크
    db_company = await company_crud.get_company_by_name(db, company_in.name)
    if db_company:
        raise HTTPException(
            status_code=400,
            detail="이미 사용 중인 회사 이름입니다"
        )
    
    # 회사 생성
    db_company = await company_crud.create_company(db, company_in)
    
    # 백그라운드에서 Admin 유저 생성
    background_tasks.add_task(
        create_admin_user,
        company_id=db_company.id,
        email=company_in.admin_email,
        password=company_in.admin_password
    )
    
    return db_company

# 다른 엔드포인트 추가 (회사 조회, 수정, 삭제 등) 