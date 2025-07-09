from ggg.models.base import GggBase
from sqlalchemy import Column, BigInteger, Text


class Place(GggBase):
    __tablename__ = "place"

    pnu = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)
    address = Column(Text, nullable=False)