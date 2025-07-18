from datetime import datetime

from ggg.schemas.base import GggBaseModel

class TokenBase(GggBaseModel):
    id: int
    user_id: int
    refresh_token: str
    created_at: datetime
    expires_at: datetime

class TokenCreate(GggBaseModel):
    user_id: int
    refresh_token: str
    created_at: datetime
    expires_at: datetime

class TokenUpdate(GggBaseModel):
    id: int
    user_id: int
    refresh_token: str
    expires_at: datetime
