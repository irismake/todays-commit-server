from datetime import datetime

from ggg.models.base import GggBase
from sqlalchemy import Column, DateTime, ForeignKey, Index, BigInteger, SmallInteger, ForeignKeyConstraint

class Grass(GggBase):
    __tablename__ = "grass"

    grass_id = Column(BigInteger, primary_key=True, autoincrement=True)
    commit_id = Column(BigInteger, ForeignKey("commit.commit_id"), nullable=False)
    cell_id = Column(SmallInteger, nullable=False)
    map_id = Column(SmallInteger, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["cell_id", "map_id"],
            ["cell.cell_id", "cell.map_id"]
        ),
        Index("idx_grass_cell", "cell_id", "map_id"),
    )

class Commit(GggBase):
    __tablename__ = "commit"

    commit_id = Column(BigInteger, primary_key=True, autoincrement=True)
    pnu = Column(BigInteger, ForeignKey("place.pnu"), nullable=False)
    user_id = Column(SmallInteger, ForeignKey("user.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        Index("idx_commit_pnu", "pnu"),
        Index("idx_commit_user_pnu", "user_id", "pnu"),
    )
