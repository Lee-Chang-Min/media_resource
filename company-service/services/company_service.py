# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from datetime import datetime
# import asyncio

# from models.model import Company
# from core.db import async_session

# async def register_company(
#     company_in: CompanyCreate,
#     db: AsyncSession,
#     background_tasks: BackgroundTasks
# ):
#     existing = await company_crud.get_company_by_name(db, company_in.name)
#     if existing:
#         raise HTTPException(status_code=400, detail="이미 사용 중인 회사 이름입니다")

#     company = await company_crud.create_company(db, company_in)

#     background_tasks.add_task(
#         create_admin_user,
#         company_id=company.id,
#         email=company_in.admin_email,
#         password=company_in.admin_password
#     )

#     return company


# async def check_premium_expiry():
#     while True:
#         async with async_session() as session:
#             # 만료된 프리미엄 플랜 찾기
#             now = datetime.utcnow()
#             result = await session.execute(
#                 select(Company).where(
#                     Company.is_premium == True,
#                     Company.premium_expiry_date <= now
#                 )
#             )
            
#             expired_companies = result.scalars().all()
            
#             # 만료된 플랜 업데이트
#             for company in expired_companies:
#                 company.is_premium = False
#                 session.add(company)
            
#             await session.commit()
        
#         # 하루에 한 번 체크
#         await asyncio.sleep(86400) 