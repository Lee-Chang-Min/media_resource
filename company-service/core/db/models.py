from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta, timezone

Base = declarative_base()

KST = timezone(timedelta(hours=9))  # 한국 시간대 정의

def kst_now():
    return datetime.now(KST)

class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    premium = Column(Boolean, default=False)
    premium_expiry_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), default=kst_now)
    updated_at = Column(DateTime(timezone=True), default=kst_now, onupdate=kst_now)