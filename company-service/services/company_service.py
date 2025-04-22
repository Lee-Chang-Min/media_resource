from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
import asyncio

from core.db.models import Company

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


import asyncio
from datetime import datetime, timezone
from sqlalchemy.future import select
from core.db.models import Company
from core.db.base import async_session  # AsyncSession 생성용 sessionmaker

async def check_plan_expiry():
    """
    하루에 한 번, 내부에서 세션을 열어 만료된 플랜을 체크·업데이트합니다.
    """
    while True:
        try:
            async with async_session() as db:
                # 만료된 프리미엄 플랜 찾기
                now = datetime.now(timezone.utc)
                result = await db.execute(
                    select(Company).where(
                        Company.premium == True,
                        Company.premium_expiry_date <= now
                    )
                )
                expired_companies: list[Company] = result.scalars().all()
                print(f"만료된 플랜 로직 실행: {len(expired_companies)}개")

                # 만료된 플랜 업데이트
                for company in expired_companies:
                    company.premium = False
                    db.add(company)

                if expired_companies:
                    await db.commit()
                    print(f"{len(expired_companies)}개 회사의 플랜이 만료되었습니다.")
                else:
                    # 변경 없더라도 세션은 닫히므로 커밋 생략 가능
                    pass

        except Exception as e:
            print(f"플랜 만료 체크 중 오류 발생: {e}")

        # 24시간 대기
        await asyncio.sleep(86400)
