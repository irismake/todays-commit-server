from pydantic import BaseModel, field_serializer
from typing import List, Optional

class LocationBase(BaseModel):
    lat: float
    lon: float

class LocationResponse(LocationBase):
    pnu: int
    address : str

    @field_serializer("pnu")
    def serialize_pnu(self, pnu: int, _info):
        return str(pnu)

class SearchLocationData(BaseModel):
    place_name: str
    address_name: str
    road_address_name: Optional[str]
    x: str
    y: str
    distance: Optional[str]