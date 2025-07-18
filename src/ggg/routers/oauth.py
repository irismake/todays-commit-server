from fastapi import APIRouter, HTTPException, Query
import httpx
import os

router = APIRouter(
    prefix="/oauth",
    tags=["oauth"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"

@router.get("/kakao/url")
async def get_kakao_login_url():
    url = (
        f"{KAKAO_AUTH_URL}"
        f"?client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
        f"&response_type=code"
    )
    return {"kakao_login_url": url}


@router.get("/kakao/callback")
async def kakao_callback(code: str = Query(...)):
    payload = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(KAKAO_TOKEN_URL, data=payload, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="카카오 토큰 요청 실패")

    token_data = res.json()
    return {
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token"),
        "expires_in": token_data.get("expires_in"),
        "token_type": token_data.get("token_type"),
        "scope": token_data.get("scope")
    }