from pydantic import BaseModel, field_serializer

class LocationBase(BaseModel):
    lat: float
    lon: float

class LocationResponse(LocationBase):
    pnu: int
    address : str

    @field_serializer("pnu")
    def serialize_pnu(self, pnu: int, _info):
        return str(pnu)
