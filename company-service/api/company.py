from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.db.schemas import CompanyBase, CompanyCreate
from core.db.base import get_db

from crud.company import get_company, create_company
# from services.company_service import register_company

router = APIRouter()


# Company 등록
@router.post("/", response_model=CompanyBase)
async def create_company(
    company_in: CompanyCreate,
    # background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # 회사 이름 중복 체크
    db_company = await get_company(db, company_in.name)
    if db_company:
        raise HTTPException(
            status_code=400,
            detail="이미 사용 중인 회사 이름입니다"
        )
    
    # 회사 생성
    db_company = await create_company(db, company_in)
    
    # 백그라운드에서 Admin 유저 생성
    # background_tasks.add_task(
    #     register_company,
    #     company_in=company_in,
    #     db=db,
    #     background_tasks=background_tasks
    # )
    
    return db_company

# Company 정보 수정 (플랜 에 대한 정보 수정을 위하여 API 필요요)
# @router.put("/{company_id}", response_model=Company)
# async def update_company(
#     company_id: int,
#     company_in: CompanyUpdate,
#     db: AsyncSession = Depends(get_db)
# ):
#     db_company = await update_company(db, company_id, company_in)
#     return db_company


# (회사 조회, 삭제 구현 생략)  