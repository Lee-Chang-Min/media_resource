import httpx
from fastapi import Header, HTTPException, status, Depends
from pydantic import BaseModel

from core.config import settings

async def get_current_user(
    authorization: str = Header(..., description="Bearer <token>")
) -> dict:
    """
    UserService의 /api/users/me (또는 /api/auth) 엔드포인트를 호출해서
    토큰 유효성 및 로그인된 사용자 정보를 가져옵니다.
    """
    url = f"{settings.USER_SERVICE_URL}/api/v1/auth"
    headers = {"Authorization": authorization}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, timeout=1.0)
    if resp.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다"
        )
    
    if resp.json()["is_admin"] == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )

    return resp.json()