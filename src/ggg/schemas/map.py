from typing import Optional
from pydantic import BaseModel
from typing import List

from ggg.schemas.base import GggBaseModel

class MapBase(GggBaseModel):
    map_id: int
    map_level: Optional[int] = None
    map_code: Optional[int] = None


class MapResponse(BaseModel):
    map_code: int
    coord_ids: List[int]

class CellBase(GggBaseModel):
    coord_id: int
    map_id: int
    zone_code: Optional[int] = None

class CoordBase(GggBaseModel):
    coord_id: int
    x: int
    y: int

class UnitBase(GggBaseModel):
    unit_code: int
    coord_id: int
    map_id: int