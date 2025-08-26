from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

from todays_commit.schemas.base import TodaysCommitBaseModel


class GrassBase(TodaysCommitBaseModel):
    grass_id: int
    commit_id: int
    coord_id: int
    map_id: int

class GrassData(BaseModel):
    coord_id: int
    commit_count: int

class GrassResponse(BaseModel):
    map_id: int
    grass_data: List[GrassData]

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

class PostResponse(BaseModel):
    message: str