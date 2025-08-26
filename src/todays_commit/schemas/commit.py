from datetime import datetime
from pydantic import BaseModel
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

class CommitResponse(BaseModel):
    commits: List[CommitData]
