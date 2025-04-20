from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from sqlalchemy.orm import validates
from dateutil.relativedelta import relativedelta

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)

class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    premium = Column(Boolean, default=False)
    premium_expiry_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
