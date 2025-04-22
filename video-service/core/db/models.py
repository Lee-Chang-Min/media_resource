from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)


class Video(Base):
    __tablename__ = "video"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)               # 중복 허용
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=False)          # 파일 경로

    company_id = Column(Integer, nullable=False)       # 회사 ID
    user_id = Column(Integer, nullable=False)          # 사용자 ID

    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)