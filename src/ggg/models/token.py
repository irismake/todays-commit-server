from ggg.models.base import GggBase
from sqlalchemy import Column, SmallInteger, String, DateTime, ForeignKey, Index
from datetime import datetime, timedelta

class Token(GggBase):
    __tablename__ = "token"

    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    user_id = Column(SmallInteger, ForeignKey("user.user_id"), nullable=False)
    refresh_token = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("idx_token_user_id", "user_id"),
    )
