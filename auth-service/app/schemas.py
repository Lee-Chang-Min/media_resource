from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    is_admin: bool = False

class UserCreate(UserBase):
    password: str
    company_id: int

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserInDB):
    pass

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: int
    exp: int
    company_id: int
    is_admin: bool 