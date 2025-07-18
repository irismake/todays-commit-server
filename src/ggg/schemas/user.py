from typing import Optional
from datetime import datetime

from ggg.schemas.base import GggBaseModel

class UserBase(GggBaseModel):
    user_id: int
    user_name: str
    email: Optional[str] = None
    provider: str
    provider_id: str
    created_at: datetime

class UserResponse(UserBase):
    access_token: str
    refresh_token: str
    refresh_token_expires_at: str