from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import httpx
from datetime import datetime, timezone
import jwt
from typing import Optional
import os
from jwt import PyJWKClient


from todays_commit.database import get_db
from todays_commit.models import User, Token
from todays_commit.schemas.oauth import AuthHandler, auth_check
from todays_commit.schemas.user import UserResponse

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")
APPLE_AUTH_KEY_URL = "https://appleid.apple.com/auth/keys"


def verify_apple_id_token(id_token: str) -> dict:
    jwk_client = PyJWKClient(APPLE_AUTH_KEY_URL)
    signing_key = jwk_client.get_signing_key_from_jwt(id_token)

    return jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=APPLE_CLIENT_ID,
        issuer="https://appleid.apple.com"
    )


@router.get("/login/kakao", response_model=UserResponse)
async def login_with_kakao(
    access_token: str = Query(...),
    db: Session = Depends(get_db)
):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        res = await client.get(KAKAO_USER_INFO_URL, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="카카오 사용자 정보 조회 실패")

    user_data = res.json()
    kakao_id = str(user_data["id"])
    nickname = user_data.get("properties", {}).get("nickname")
    email = user_data.get("kakao_account", {}).get("email")

    user = db.query(User).filter_by(provider_id=kakao_id).first()
    if not user:
        user = User(provider="kakao", provider_id=kakao_id, user_name=nickname, email=email)
        db.add(user)
    else:
        # 탈퇴했던 유저 복구
        if not user.is_active:
            user.is_active = True
        user.user_name = nickname
        user.email = email

    db.commit()
    db.refresh(user)

    access_token = AuthHandler().create_access_token(user.user_id)
    token_model = Token.create_or_update_refresh_token(db, user.user_id)

    return UserResponse(
        access_token=access_token,
        refresh_token=token_model.refresh_token,
        refresh_token_expires_at=token_model.expires_at.isoformat(),
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        provider=user.provider,
        provider_id=user.provider_id,
        created_at=user.created_at.isoformat()
    )

@router.get("/login/apple", response_model=UserResponse)
async def login_with_apple(
    id_token: str = Query(...),
    user_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        decoded = verify_apple_id_token(id_token)
    except Exception:
        raise HTTPException(status_code=400, detail="유효하지 않은 id_token입니다.")
    
    provider_id = decoded["sub"]
    email = decoded.get("email", "")

    user = db.query(User).filter_by(provider="apple", provider_id=provider_id).first()
    if not user:
        if not user_name or not user_name.strip():
            raise HTTPException(status_code=400, detail="최초 로그인 시 user_name 필요")
        user = User(provider="apple", provider_id=provider_id, user_name=user_name, email=email)
        db.add(user)
    else:
        # 탈퇴했던 유저 복구
        if not user.is_active:
            user.is_active = True
        user.email = email
    db.commit()
    db.refresh(user)

    access_token = AuthHandler().create_access_token(user.user_id)
    token_model = Token.create_or_update_refresh_token(db, user.user_id)

    return UserResponse(
        access_token=access_token,
        refresh_token=token_model.refresh_token,
        refresh_token_expires_at=token_model.expires_at.isoformat(),
        user_id=user.user_id,
        user_name=user.user_name,
        email=user.email,
        provider=user.provider,
        provider_id=user.provider_id,
        created_at=user.created_at.isoformat()
    )


@router.post("/logout")
async def logout_user(
    user_id: int = Depends(auth_check),
    db: Session = Depends(get_db)
):
    token = db.query(Token).filter(Token.user_id == user_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="로그인된 토큰이 없습니다.")

    token.expires_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "성공적으로 로그아웃되었습니다."}

@router.get("/leave")
async def leave_user(
    user_id: int = Depends(auth_check),
    db: Session = Depends(get_db)
):
    user: User = User.find_by_id(db, user_id)
    user.is_active = False
    db.commit()
    return {"message": "성공적으로 회원이 탈퇴되었습니다."}