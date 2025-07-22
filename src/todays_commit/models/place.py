from todays_commit.models.base import TodaysCommitBase
from sqlalchemy import Column, BigInteger, Text, Float


class Place(TodaysCommitBase):
    __tablename__ = "place"

    pnu = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)
    address = Column(Text, nullable=False)
    x =Column(Float, nullable=False)
    y = Column(Float, nullable=False)