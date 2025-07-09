from ggg.schemas.base import GggBaseModel

class PlaceBase(GggBaseModel):
    pnu: int
    name: str
    address: str