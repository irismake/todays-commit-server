from sqlalchemy import Column, SmallInteger, String, DateTime, ForeignKey, Index
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Union

from ggg.models.base import GggBase
from ggg.schemas.oauth import AuthHandler
from ggg.schemas.token import TokenCreate, TokenUpdate
from ggg.exception import ExpiredTokenException


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

    @classmethod
    def upsert(cls, db: Session, token_info: Union[TokenCreate, TokenUpdate]):
        obj = None
        token_id = getattr(token_info, "id", None)
        if token_id:
            obj = db.query(cls).filter_by(id=token_id).first()
        if not obj:
            obj = cls()

        obj.user_id = token_info.user_id
        obj.refresh_token = token_info.refresh_token
        obj.expires_at = token_info.expires_at

        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @classmethod
    def find_by_userid(cls, db: Session, user_id: int):
        return db.query(cls).filter_by(user_id=user_id).order_by(cls.id.desc()).first()

    @classmethod
    def create_or_update_refresh_token(cls, db: Session, user_id: int) -> "Token":
        auth = AuthHandler()
        token = cls.find_by_userid(db, user_id)
        now = datetime.now()
        expires_at = now + auth.refresh_expires
        
        if token is None:
            refresh_token = AuthHandler().create_refresh_token(user_id)
            token_model = TokenCreate.model_validate({
                "user_id": user_id,
                "refresh_token": refresh_token,
                "created_at": now,
                "expires_at": expires_at,
            })
            return cls.upsert(db, token_model)

        try:
            AuthHandler().decode_token(token.refresh_token)
        except ExpiredTokenException:
            refresh_token = AuthHandler().create_refresh_token(user_id)
            token_model = TokenUpdate.model_validate({
                "id": token.id,
                "user_id": user_id,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
            })
            return cls.upsert(db, token_model)

        return token
