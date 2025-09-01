from datetime import datetime
from pydantic import BaseModel, field_serializer
from typing import List, Optional

from todays_commit.schemas.base import TodaysCommitBaseModel


class CommitBase(TodaysCommitBaseModel):
    commit_id: int
    pnu: int
    user_id: int
    created_at: datetime

class CommitData(BaseModel):
    commit_id: int
    user_name: Optional[str] = None
    created_at: datetime
    pnu: Optional[int] = None
    place_name: Optional[str] = None
    address: Optional[str] = None

    @field_serializer("pnu")
    def serialize_pnu(self, pnu: int, _info):
        return str(pnu)

class CommitResponse(BaseModel):
    next_cursor: Optional[int]
    commits: List[CommitData]
