from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from todays_commit.schemas.base import TodaysCommitBaseModel

class UserBase(TodaysCommitBaseModel):
    user_id: int
    user_name: str
    email: Optional[str] = None
    provider: str
    provider_id: str
    created_at: datetime

class UserData(BaseModel):
    user_name: str
    provider: str

class UserResponse(UserBase):
    access_token: str
    refresh_token: str
    refresh_token_expires_at: str