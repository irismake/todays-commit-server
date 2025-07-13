from typing import Optional

from ggg.schemas.base import GggBaseModel

class MapBase(GggBaseModel):
    map_id: int
    map_level: Optional[int] = None
    map_code: Optional[int] = None

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