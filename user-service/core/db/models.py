from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    company_id = Column(Integer, nullable=False)
    is_admin = Column(Boolean, default=False)

    name = Column(String, nullable=False)
    phoneNumber = Column(String, nullable=True)

    point = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, nullable=False, unique=True)

    # 어떤 사용자에게 발급된 것인지
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref="refresh_tokens")

    # 토큰 만료 시점
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # 토큰을 무효화했는지 여부 (ex: 로그아웃)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    def is_active(self) -> bool:
        return self.revoked_at is None and self.expires_at > utc_now()
