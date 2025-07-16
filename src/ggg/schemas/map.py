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
    zone_code: Optional[int] = None

class CellData(BaseModel):
    coord_id: int
    zone_code: int

class MapBase(GggBaseModel):
    map_id: int
    map_level: Optional[int] = None
    map_code: Optional[int] = None


class MapResponse(BaseModel):
    map_code: int
    map_data: List[CellData]


class CoordBase(GggBaseModel):
    coord_id: int
    x: int
    y: int