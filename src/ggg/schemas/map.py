from typing import Optional
from pydantic import BaseModel
from typing import List

from ggg.schemas.base import GggBaseModel

class UnitBase(GggBaseModel):
    unit_code: int
    coord_id: int
    map_id: int

class CellBase(GggBaseModel):
    coord_id: int
    map_id: int
    zone_code: int

class CellData(BaseModel):
    map_level: int
    map_id: int
    coord_id: int

class CellResponse(BaseModel):
    pnu: int
    maps: List[CellData]

class MapBase(GggBaseModel):
    map_id: int
    map_level: Optional[int] = None
    map_code: Optional[int] = None

class MapData(BaseModel):
    coord_id: int
    zone_code: int

class MapResponse(BaseModel):
    map_code: int
    map_data: List[MapData]

class CoordBase(GggBaseModel):
    coord_id: int
    x: int
    y: int