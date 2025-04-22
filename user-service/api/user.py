import asyncio
from sqlalchemy.exc import OperationalError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from core.config import settings
from core.db.base import get_db
from core.db.models import User
from core.db.schemas import Token
from core.db.schemas import UserBase, UserCreate, LoginRequest, UserUpdate

from api.deps import get_current_user
from crud.user import auth_user, check_email_exists, create_user_db, get_user_by_id, update_user_db, delete_user_db, get_users_db, award_points_db
from core.auth import create_access_token, create_refresh_token, verify_refresh_token
from crud.token import token_revoke

router = APIRouter()

@router.post("/login", response_model=Token)
async def login( login_request: LoginRequest, db: AsyncSession = Depends(get_db)):

    try:
        user = await auth_user(db, login_request.company_name, login_request.email, login_request.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 이메일 또는 비밀번호입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(
            data = {
                "sub": str(user.id),
                "company_id": user.company_id,
                "is_admin": user.is_admin,
            },
            expires_delta=timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        )
        
        refresh_token = await create_refresh_token(
            db = db,
            user_id = str(user.id),
            company_id = user.company_id,
            is_admin = user.is_admin,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
    
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/users", response_model=UserBase)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):

    # 이메일 중복 체크 (회사가 다르면 중복이 가능하나, 같은 회사일 경우 이메일 중복 불가.)
    if await check_email_exists(db, user_in.email, user_in.company_id):
        raise HTTPException(
            status_code=400,
            detail="이메일이 이미 사용 중입니다"
        )
    
    # 초기 비밀번호는 이메일 주소와 동일하게 설정 (화면에서 최초 로그인 시 비밀번호 변경 API 호출)
    user = await create_user_db(
        db,
        user_in.email,
        user_in.email,   
        user_in.company_id,
        user_in.is_admin,
        user_in.name,
        user_in.phoneNumber
    )

    return user

# 로그아웃
@router.post("/logout")
async def logout(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):  
    
    # 리프레시 토큰 무효화
    await token_revoke(db, None, int(current_user.id))

    return {"message": "로그아웃 되었습니다"}


# User List
@router.get("/users")
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:    
        # 같은 Company의 User List
        users = await get_users_db(db, current_user.company_id)

        # 필요한 필드만 포함하여 응답 데이터 구성 (추 후 페이징 처리도 필요 함)
        filtered_users = []
        for user in users:
            filtered_users.append({
                "email": user.email,
                "id": user.id,
                "name": user.name,
                "point": user.point,
                "is_admin": user.is_admin,
                "company_id": user.company_id,
                "phoneNumber": user.phoneNumber,
            })
        
        return filtered_users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )

# User Update
@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    # 0일 경우 자신의 정보를 수정하는 것으로 간주
    if user_id == 0:
        user_id = current_user.id

    # 수정할 사용자 조회
    update_user = await get_user_by_id(db, int(user_id))

    if not update_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    # 수정할 사용자 정보 조회 (admin 권한이 있거나 자신의 정보를 수정할 경우 가능, 토큰에 담겨있는 userid가 본인 이 맞는지도 한번 더 확인인)
    if current_user.id == str(update_user.id) or (
        current_user.is_admin and 
        current_user.company_id == update_user.company_id
    ):
        
        # 관리자 권한이 없는 사용자가 관리자 권한을 수정하려고 할 경우 예외 발생
        if(current_user.is_admin is False and user_in.is_admin is True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없으므로 관리자 권한을 수정할 수 없습니다"
            )

        success = await update_user_db(db, update_user, user_in)

        if success:
            return {"message": "사용자 정보가 성공적으로 수정되었습니다"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 정보 수정 중 오류가 발생했습니다"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 작업을 수행할 권한이 없습니다"
        )
    

# User Delete
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # 0일 경우 자신의 정보를 삭제하는 것으로 간주
    if user_id == 0:
        user_id = current_user.id
    
    delete_user = await get_user_by_id(db, int(user_id)) # current_user.id 가 STRING 형이므로 형변환 필요
    #delete_user.id 는 int 

    # 삭제할 사용자 정보 조회
    if not delete_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    # 삭제할 사용자 정보 조회 (admin 권한이 있거나 자신의 정보를 삭제할 경우 가능)
    if current_user.id == str(delete_user.id) or (
        current_user.is_admin and 
        current_user.company_id == delete_user.company_id
        ):

        success = await delete_user_db(db, delete_user.id)
        
        if success:
            return {"message": "사용자가 성공적으로 삭제되었습니다"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 삭제 중 오류가 발생했습니다"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 작업을 수행할 권한이 없습니다"
        )

# 로그인된 사용자 확인
@router.get("/auth")
async def auth(
    current_user: User = Depends(get_current_user)
):
    try:
        return current_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인인 확인 중 오류가 발생했습니다: {str(e)}"
        )


#refresh token 검증 후 access token 발급
@router.post("/token/access")
async def token(
    refresh_token: str ,
    db: AsyncSession = Depends(get_db)
):
    # 1) Refresh Token 검증
    result = await verify_refresh_token(db, refresh_token)

    # 2) 기존 refresh token 무효화
    await token_revoke(db, refresh_token)

    # 3) 새 Access/Refresh Token 발급
    if (result):
        access_token = create_access_token(
            data = {
                "sub": str(result["sub"]),
                "company_id": result["company_id"],
                "is_admin": result["is_admin"],
            },
            expires_delta=timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
        )
        
        refresh_token = await create_refresh_token(
            db = db,
            user_id = str(result["sub"]),
            company_id = result["company_id"],
            is_admin = result["is_admin"],
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# 포인트 부과
@router.post("/points")
async def award_points(
    user_id: int,
    points: int,
    db: AsyncSession = Depends(get_db)
):
    """
    사용자에게 포인트를 부여하는 API.
    Video Service에서 호출할 때 JSON 바디로 user_id와 points를 전달.
    """
    try:
        # award_points 내부에서 Pessimistic Lock & lock_timeout 설정이 적용됩니다.
        await award_points_db(db, user_id, points)

    except asyncio.TimeoutError:
        # lock_timeout을 초과한 경우
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lock timeout: 잠시 후 다시 시도해주세요"
        )
    except OperationalError as e:
        # FOR UPDATE NOWAIT 실패 등 DB 관련 오류
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"DB lock error: {e.orig if hasattr(e, 'orig') else str(e)}"
        )
    except Exception as e:
        # 기타 예외
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"포인트 부여 중 오류가 발생했습니다: {e}"
        )

    return {"msg": "포인트 부여 완료", "success": True}