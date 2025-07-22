from pydantic import BaseModel

class LocationBase(BaseModel):
    lat: float
    lon: float

class LocationResponse(LocationBase):
    pnu: int
