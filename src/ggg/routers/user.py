from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import httpx

from ggg.database import get_db
from ggg.models import User, Token
from ggg.schemas.oauth import AuthHandler
from ggg.schemas.user import UserResponse

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

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