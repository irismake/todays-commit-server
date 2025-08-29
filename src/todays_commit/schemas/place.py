from pydantic import BaseModel, field_serializer
from typing import List, Optional

from todays_commit.schemas.base import TodaysCommitBaseModel
from todays_commit.schemas.commit import CommitData


class PlaceBase(TodaysCommitBaseModel):
    pnu: int
    name: str
    address: str
    x: float
    y: float

    @field_serializer("pnu")
    def serialize_pnu(self, pnu: int, _info):
        return str(pnu)

class PlaceData(BaseModel):
    pnu: int
    name: str
    x: float
    y: float
    commit_count: int

    @field_serializer("pnu")
    def serialize_pnu(self, pnu: int, _info):
        return str(pnu)

class PlaceResponse(BaseModel):
    next_cursor: Optional[str]
    places: List[PlaceData]

class PlaceDetailResponse(PlaceBase):
    commits: List[CommitData]

class PlaceCheck(BaseModel):
    exists: bool
    name: Optional[str] = None