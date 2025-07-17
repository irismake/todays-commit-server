from datetime import datetime
from pydantic import BaseModel
from typing import List

from ggg.schemas.base import GggBaseModel


class GrassBase(GggBaseModel):
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

class CommitBase(GggBaseModel):
    commit_id: int
    pnu: int
    user_id: int
    created_at: datetime

class CommitData(BaseModel):
    user_name: str
    created_at: datetime