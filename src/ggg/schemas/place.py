from pydantic import BaseModel, field_serializer
from typing import List
from ggg.schemas.base import GggBaseModel

class PlaceBase(GggBaseModel):
    pnu: int
    name: str
    address: str

class PlaceData(BaseModel):
    pnu: int
    name: str
    distance : float
    commit_count: int

    @field_serializer("pnu")
    def serialize_pnu(self, pnu: int, _info):
        return str(pnu)

class PlaceResponse(BaseModel):
    places: List[PlaceData]