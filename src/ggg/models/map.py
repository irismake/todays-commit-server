from ggg.models.base import GggBase
from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, BigInteger, Index, ForeignKeyConstraint


class Map(GggBase):
    __tablename__ = "map"

    map_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    map_level = Column(SmallInteger)
    map_code = Column(BigInteger)

class Coord(GggBase):
    __tablename__ = "coord"

    x = Column(SmallInteger, primary_key=True)
    y = Column(SmallInteger, primary_key=True)

class Cell(GggBase):
    __tablename__ = "cell"
    
    cell_id = Column(SmallInteger, primary_key=True)
    map_id = Column(SmallInteger, ForeignKey("map.map_id"), primary_key=True)

    zone_code = Column(Integer)
    x = Column(SmallInteger)
    y = Column(SmallInteger)

    __table_args__ = (
        ForeignKeyConstraint(["x", "y"], ["coord.x", "coord.y"]),
    )

class Unit(GggBase):
    __tablename__ = "unit"

    unit_code = Column(BigInteger, primary_key=True)
    cell_id = Column(SmallInteger, nullable=False)
    map_id = Column(SmallInteger, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["cell_id", "map_id"],
            ["cell.cell_id", "cell.map_id"]
        ),
        Index("idx_unit_cell", "cell_id", "map_id"),
    )