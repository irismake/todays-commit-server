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
from todays_commit.schemas.user import UserResponse, UserData
from todays_commit.schemas.base import PostResponse

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"
KAKAO_DISCONNECT_URL = "https://kapi.kakao.com/v1/user/unlink"
KAKAO_ADMIN_KEY = os.getenv("KAKAO_ADMIN_KEY")

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
    is_first_login = False

    if not user:
        user = User(provider="kakao", provider_id=kakao_id, user_name=nickname, email=email)
        db.add(user)
        is_first_login = True
    else:
        if not user.is_active:
            restored_name = user.user_name
            new_user = User(
                provider="kakao",
                provider_id=kakao_id,
                user_name=restored_name,
                email=email
            )
            db.add(new_user)
            user = new_user
            is_first_login = True
        else:
            user.user_name = nickname
            user.email = email

    db.commit()
    db.refresh(user)

    access_token = AuthHandler().create_access_token(user.user_id)
    _ = Token.create_or_update_refresh_token(db, user.user_id)

    return UserResponse(
        user_name=user.user_name,
        email=user.email,
        provider=user.provider,
        created_at=user.created_at.isoformat(),
        access_token=access_token,
        is_first_login=is_first_login
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
    is_first_login = False

    user = db.query(User).filter_by(provider="apple", provider_id=provider_id).first()
    if not user:
        if not user_name or not user_name.strip():
            raise HTTPException(status_code=400, detail="최초 로그인 시 user_name 필요")
        user = User(provider="apple", provider_id=provider_id, user_name=user_name, email=email)
        db.add(user)
        is_first_login = True
    else:
        if not user.is_active:
            restored_name = user.user_name
            new_user = User(
                provider="apple",
                provider_id=provider_id,
                user_name=restored_name,
                email=email
            )
            db.add(new_user)
            user = new_user
            is_first_login = True
        else:
            user.email = email

    db.commit()
    db.refresh(user)

    access_token = AuthHandler().create_access_token(user.user_id)
    _ = Token.create_or_update_refresh_token(db, user.user_id)

    return UserResponse(
        user_name=user.user_name,
        email=user.email,
        provider=user.provider,
        created_at=user.created_at.isoformat(),
        access_token=access_token,
        is_first_login=is_first_login
    )

@router.get("/info", response_model=UserData, dependencies=[Depends(auth_check)])
async def get_user_info(
    user_id: int = Depends(auth_check),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    return UserData(
        user_name=user.user_name,
        provider=user.provider
    )


@router.post("/logout", response_model=PostResponse, dependencies=[Depends(auth_check)])
async def logout_user(
    user_id: int = Depends(auth_check),
    db: Session = Depends(get_db)
):
    token = db.query(Token).filter(Token.user_id == user_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="로그인된 토큰이 없습니다.")

    token.expires_at = datetime.now(timezone.utc)
    db.commit()

    return PostResponse(
        message = "Success",
    )


@router.post("/leave", response_model=PostResponse, dependencies=[Depends(auth_check)])
async def leave_user(
    user_id: int = Depends(auth_check),
    db: Session = Depends(get_db)
):
    user: User = User.find_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    if not user.provider_id:
        raise HTTPException(status_code=400, detail="provider_id가 없습니다.")

    if user.provider == "kakao":
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            "Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}"
        }
        data = {
            "target_id_type": "user_id",
            "target_id": user.provider_id
        }

        async with httpx.AsyncClient() as client:
            res = await client.post(KAKAO_DISCONNECT_URL, headers=headers, data=data)

        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=f"카카오 unlink 실패: {res.text}")
    user.is_active = False
    db.commit()
    
    return PostResponse(
        message = "Success",
    )