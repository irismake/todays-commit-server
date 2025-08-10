from typing import Optional
from pydantic import BaseModel
from typing import List

from todays_commit.schemas.base import TodaysCommitBaseModel

class UnitBase(TodaysCommitBaseModel):
    unit_code: int
    coord_id: int
    map_id: int

class CellBase(TodaysCommitBaseModel):
    coord_id: int
    map_id: int
    zone_code: int

class CellData(BaseModel):
    coord_id: int
    zone_code: int

class CellResponse(BaseModel):
    map_level: int
    map_id: int
    cell_data: CellData

class MapBase(TodaysCommitBaseModel):
    map_id: int
    map_level: Optional[int] = None
    map_code: Optional[int] = None

class MapData(BaseModel):
    coord_id: int
    zone_code: int

class MapResponse(BaseModel):
    map_code: int
    map_data: List[MapData]

class CoordBase(TodaysCommitBaseModel):
    coord_id: int
    x: int
    y: int