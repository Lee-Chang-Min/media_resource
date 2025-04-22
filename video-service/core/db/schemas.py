from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Video(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    file_path: str
    company_id: int
    user_id: int
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class VideoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    file_path: str
    company_id: int
    user_id: int
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
