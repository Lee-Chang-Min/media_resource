from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Video(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    file_path: str
    company_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class VideoCreate(BaseModel):
    name: str
    description: Optional[str] = None
    file_path: str
    company_id: int
    user_id: int
