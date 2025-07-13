from ggg.models.base import GggBase
from sqlalchemy import Column, PrimaryKeyConstraint, Integer, SmallInteger, BigInteger, Index, ForeignKeyConstraint


class Map(GggBase):
    __tablename__ = "map"

    map_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    map_level = Column(SmallInteger)
    map_code = Column(BigInteger)

class Coord(GggBase):
    __tablename__ = "coord"

    coord_id = Column(SmallInteger, primary_key=True)
    x = Column(SmallInteger)
    y = Column(SmallInteger)


class Cell(GggBase):
    __tablename__ = "cell"

    coord_id = Column(SmallInteger, nullable=False)
    map_id = Column(SmallInteger, nullable=False)
    zone_code = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint("coord_id", "map_id"),
        ForeignKeyConstraint(["coord_id"], ["coord.coord_id"]),
        ForeignKeyConstraint(["map_id"], ["map.map_id"]),
    )

class Unit(GggBase):
    __tablename__ = "unit"

    unit_code = Column(BigInteger, primary_key=True)
    coord_id = Column(SmallInteger, nullable=False)
    map_id = Column(SmallInteger, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["coord_id", "map_id"],
            ["cell.coord_id", "cell.map_id"]
        ),
        Index("idx_unit_cell", "coord_id", "map_id"),
    )