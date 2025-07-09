from typing import Optional

from ggg.schemas.base import GggBaseModel

class MapBase(GggBaseModel):
    map_id: int
    map_level: Optional[int] = None
    map_code: Optional[int] = None

class CellBase(GggBaseModel):
    cell_id: int
    map_id: int
    zone_code: Optional[int] = None
    x: int
    y: int

class CoordBase(GggBaseModel):
    x: int
    y: int

class UnitBase(GggBaseModel):
    unit_code: int
    cell_id: int
    map_id: int