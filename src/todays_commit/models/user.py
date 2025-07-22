from todays_commit.models.base import TodaysCommitBase
from sqlalchemy.orm import Session

from sqlalchemy import Column, SmallInteger, String, DateTime, Index, Boolean
from datetime import datetime

class User(TodaysCommitBase):
    __tablename__ = "user"

    user_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    user_name = Column(String(255), nullable=False)
    email = Column(String(255))
    provider = Column(String(20), nullable=False)
    provider_id = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index("uq_user_provider_id", "provider", "provider_id", unique=True),
    )

    @classmethod
    def find_by_id(cls, db: Session, id: int):
        return db.query(cls).filter(User.user_id == id).first()

    @classmethod
    def check_activate(cls, db: Session, user_id: int) -> bool:
        user = cls.find_by_id(db, user_id)
        return bool(user and user.is_active)