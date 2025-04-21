from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re

class UserBase(BaseModel):
    email: EmailStr
    is_admin: bool = False

class UserCreate(UserBase):
    company_id: int
    name: str
    phoneNumber: str

    @field_validator('phoneNumber')
    def validate_phone_number(cls, v):
        pattern = r'^01[0-9]{8,9}$'  # 010XXXXXXXX 또는 01XXXXXXXXX 형식
        if not re.match(pattern, v):
            raise ValueError('전화번호는 01012341234 형식이어야 합니다')
        return v


class UserUpdate(BaseModel):
    is_admin: Optional[bool] = None
    name: Optional[str] = None
    phoneNumber: Optional[str] = None


class UserInDB(UserBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str    
    exp: int
    company_id: int
    is_admin: bool 

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
