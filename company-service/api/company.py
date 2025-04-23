import httpx
from fastapi import status, Query
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.schemas import CompanyCreate, CompanyCreateResponse, CompanyUpdate

from core.db.base import get_db
from core.dep import get_current_user
from crud.company import get_company, create_company, delete_company, update_company_db, get_company_plan_db
from core.config import settings

router = APIRouter()

#health check
@router.get("/health")
async def health_check():
    return {"status": "ok"}

#Company Name 조회
@router.get(
        "/",
        summary="회사 이름 조회",
        description="회사 이름으로 회사의 고유 ID를 조회합니다.",
        response_model=int,
        status_code=status.HTTP_200_OK,
        responses={
            500: {"description": "서버 에러 발생"}
        }        
)
async def get_company_name(
    company: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await get_company(db, company)

        if result is None:
            return None
        
        return result.id
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회사 이름 조회 중 오류가 발생했습니다: {str(e)}"
        )
    
#Company Plan 조회
@router.get(
        "/premium/{company_id}",
        summary="회사 플랜 조회",
        description="회사 ID를 기반으로 회사의 플랜 정보를 조회합니다.",
        response_model=bool,
        status_code=status.HTTP_200_OK,
        responses={
            400: {"description": "회사 ID가 없습니다"},
            500: {"description": "서버 에러 발생"}
        }
)
async def get_company_plan(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:

        result = await get_company_plan_db(db, company_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="회사 ID가 없습니다"
            )
        
        return result.premium
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회사 플랜 조회 중 오류가 발생했습니다: {str(e)}"
        )


# Company 등록 Router
@router.post(
        "/create", 
        summary="회사 생성 후 관리자 계정 리턴",
        description="신규 회사를 등록하고, 관리자 계정을 유저 서비스에 생성 요청 합니다.",
        response_model=CompanyCreateResponse,
        status_code=status.HTTP_200_OK,
        responses={
            400: {"description": "이미 사용 중인 회사 이름입니다"},
            500: {"description": "회사 생성 중 오류가 발생했습니다"},
            502: {"description": "유저 서비스 호출 실패"}
        }
)
async def create_company_api(
    company_in: CompanyCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 회사 이름 중복 체크
        db_company = await get_company(db, company_in.company_name)
        if db_company:
            raise HTTPException(
                status_code=400,
                detail="이미 사용 중인 회사 이름입니다"
            )
    
        # 회사 ID 생성을 위해 우선 Company 생성
        db_company = await create_company(db, company_in)
        
        # 유저 서비스 호출: 관리자 계정 생성
        user_payload = {
            "email": company_in.email,
            "password": company_in.email, # 초기 비밀번호 이메일과 동일
            "company_id": db_company.id,
            "is_admin": True,
            "name": company_in.user_name,
            "phoneNumber": company_in.user_phone_number 
        }

        async with httpx.AsyncClient(base_url=settings.USER_SERVICE_URL) as client:
            resp = await client.post("/v1/users", json=user_payload)
            if resp.status_code != status.HTTP_200_OK:
                # 발급 실패 시 생성 했던 Company 삭제
                await delete_company(db, db_company.id)

                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"유저 서비스 호출 실패: {resp.text}"
                )

        return CompanyCreateResponse(   
            msg="회사 생성 성공하여 Email과 Password를 발급합니다.",
            result=True,
            email=company_in.email,
            password=company_in.email
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회사 생성 중 오류가 발생했습니다 > {str(e)}"
        )



# Company 정보 수정 (유료 무료 플랜에 대한 정보 수정을 위하여 API 필요)
@router.put(
        "/update",
        summary="회사 정보 수정",
        description="회사의 플랜 정보를 수정 합니다.",
        response_model=None,
        status_code=status.HTTP_200_OK,
        responses={
            500: {"description": "회사 정보 수정 중 오류가 발생했습니다"},
            403: {"description": "관리자 권한이 없습니다"}
        }
)
async def update_company(
    company_in: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    try:
        # 회사 정보 수정
        db_company = await update_company_db(db, int(current_user["company_id"]), company_in)

        return db_company
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회사 정보 수정 중 오류가 발생했습니다 > {str(e)}"
        )


# (회사 삭제 구현 생략)  