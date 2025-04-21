from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    premium: bool = False

class CompanyCreate(CompanyBase):
    email: EmailStr
    premium_expiry_date: Optional[Literal[1, 3, 12]] = None

    @field_validator('premium_expiry_date', mode='before')
    def ensure_months_if_premium(cls, v, info):
        # premium=True면 months를 안 보내도 기본 1개월
        if info.data.get('premium') and v is None:
            return 1
        return v

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    premium: Optional[bool] = None
    premium_expiry_date: Optional[datetime] = None

class CompanyInDB(CompanyBase):
    id: str
    premium_expiry_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

