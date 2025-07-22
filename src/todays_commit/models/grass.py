from datetime import datetime

from todays_commit.models.base import TodaysCommitBase
from sqlalchemy import Column, DateTime, ForeignKey, Index, BigInteger, SmallInteger, ForeignKeyConstraint

class Grass(TodaysCommitBase):
    __tablename__ = "grass"

    grass_id = Column(BigInteger, primary_key=True, autoincrement=True)
    commit_id = Column(BigInteger, ForeignKey("commit.commit_id"), nullable=False)
    coord_id = Column(SmallInteger, nullable=False)
    map_id = Column(SmallInteger, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["coord_id", "map_id"],
            ["cell.coord_id", "cell.map_id"]
        ),
        Index("idx_grass_cell", "coord_id", "map_id"),
    )

class Commit(TodaysCommitBase):
    __tablename__ = "commit"

    commit_id = Column(BigInteger, primary_key=True, autoincrement=True)
    pnu = Column(BigInteger, ForeignKey("place.pnu"), nullable=False)
    user_id = Column(SmallInteger, ForeignKey("user.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        Index("idx_commit_pnu", "pnu"),
        Index("idx_commit_user_pnu", "user_id", "pnu"),
    )
