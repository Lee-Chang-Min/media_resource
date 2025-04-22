from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal
from datetime import datetime
import re

class CompanyBase(BaseModel):
    company_name: str
    premium: bool = False

class CompanyCreate(CompanyBase):
    email: EmailStr
    user_name: str
    user_phone_number: str
    premium_expiry_date: Optional[Literal[1, 3, 12]] = None

    @field_validator('user_phone_number')
    def validate_phone_number(cls, v):
        pattern = r'^01[0-9]{8,9}$'  # 010XXXXXXXX 또는 01XXXXXXXXX 형식
        if not re.match(pattern, v):
            raise ValueError('전화번호는 01012341234 형식이어야 합니다')
        return v

    @field_validator('premium_expiry_date', mode='before')
    def ensure_months_if_premium(cls, v, info):
        # premium=True면 months를 안 보내도 기본 1개월
        if info.data.get('premium') and v is None:
            return 1
        if not info.data.get('premium') and v is not None:
            raise ValueError("premium이 False일 경우 premium_expiry_date를 설정할 수 없습니다")
        return v

class CompanyUpdate(BaseModel):
    premium: Optional[bool] = None
    premium_expiry_date: Optional[Literal[1, 3, 12]] = None


class CompanyInDB(CompanyBase):
    id: int
    premium_expiry_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class CompanyCreateResponse(BaseModel):
    msg: str
    result: bool
    email: str
    password: str
