from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    premium: bool = False

class CompanyCreate(CompanyBase):
    email: EmailStr
    premium_expiry_date: Optional[datetime] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    premium: Optional[bool] = None
    premium_expiry_date: Optional[datetime] = None

# class CompanyInDB(CompanyBase):
#     id: int
#     premium_expiry_date: Optional[datetime] = None
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         orm_mode = True

