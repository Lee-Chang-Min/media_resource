from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    is_premium: bool = False

class CompanyCreate(CompanyBase):
    admin_email: EmailStr
    admin_password: str
    premium_expiry_date: Optional[datetime] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    is_premium: Optional[bool] = None
    premium_expiry_date: Optional[datetime] = None

class CompanyInDB(CompanyBase):
    id: int
    premium_expiry_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Company(CompanyInDB):
    pass 