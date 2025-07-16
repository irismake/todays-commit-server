from ggg.models.base import GggBase
from sqlalchemy import Column, BigInteger, Text, Float


class Place(GggBase):
    __tablename__ = "place"

    pnu = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)
    address = Column(Text, nullable=False)
    x =Column(Float, nullable=False)
    y = Column(Float, nullable=False)