from fastapi import APIRouter, Depends,HTTPException, Query
from sqlalchemy.orm import Session
import httpx

from ggg.database import get_db
from ggg.models.user import User
from ggg.utils.jwt import create_jwt_token

router = APIRouter(
    prefix="/oauth",
    tags=["oauth"]
)

KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"


@router.get("/login/kakao")
async def login_with_kakao_token(
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

    # DB에서 유저 조회 또는 생성
    user = db.query(User).filter_by(provider_id=kakao_id).first()
    if not user:
        user = User(provider="kakao", provider_id=kakao_id, user_name=nickname, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    # JWT 발급
    jwt_token = create_jwt_token(user.user_id)

    return {
        "jwt_token": jwt_token,
        "user_id": user.user_id,
        "provider": user.provider,
        "provider_id": user.provider_id,
        "user_name": user.user_name,
        "email": user.email,
    }
