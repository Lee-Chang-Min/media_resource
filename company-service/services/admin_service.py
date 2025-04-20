# import httpx
# from app.core.config import settings

# async def create_admin_user(company_id: int, email: str, password: str):
#     # Auth 서비스에 요청 보내기
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(
#                 f"{settings.AUTH_SERVICE_URL}/users",
#                 json={
#                     "email": email,
#                     "password": password,
#                     "company_id": company_id,
#                     "is_admin": True
#                 }
#             )
#             response.raise_for_status()
#         except httpx.HTTPStatusError as e:
#             print(f"Admin 유저 생성 실패: {e}") 