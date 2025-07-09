from ggg.models.base import GggBase

from sqlalchemy import Column, SmallInteger, String, DateTime, Index
from datetime import datetime

class User(GggBase):
    __tablename__ = "user"

    user_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    user_name = Column(String(255), nullable=False)
    email = Column(String(255))
    provider = Column(String(20), nullable=False)
    provider_id = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        Index("uq_user_provider_id", "provider", "provider_id", unique=True),
    )