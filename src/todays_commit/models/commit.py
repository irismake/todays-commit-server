from datetime import datetime

from todays_commit.models.base import TodaysCommitBase
from sqlalchemy import Column, ForeignKey, DateTime, Index, BigInteger, SmallInteger

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
