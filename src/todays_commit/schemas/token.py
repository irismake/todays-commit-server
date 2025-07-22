from datetime import datetime

from todays_commit.schemas.base import TodaysCommitBaseModel

class TokenBase(TodaysCommitBaseModel):
    id: int
    user_id: int
    refresh_token: str
    created_at: datetime
    expires_at: datetime

class TokenCreate(TodaysCommitBaseModel):
    user_id: int
    refresh_token: str
    created_at: datetime
    expires_at: datetime

class TokenUpdate(TodaysCommitBaseModel):
    id: int
    user_id: int
    refresh_token: str
    expires_at: datetime
