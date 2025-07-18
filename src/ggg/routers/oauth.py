from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import httpx
import os
from urllib.parse import urlencode

router = APIRouter(
    prefix="/oauth",
    tags=["oauth"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"

@router.get("/kakao/url")
async def get_kakao_login_url():
    url = (
        f"{KAKAO_AUTH_URL}"
        f"?client_id={KAKAO_CLIENT_ID}"
        f"&redirect_uri={KAKAO_REDIRECT_URI}"
        f"&response_type=code"
        f"&prompt=login"
    )
    return {"kakao_login_url": url}


@router.get("/kakao/callback")
async def kakao_callback(code: str = Query(...)):
    payload = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code,
        "client_secret": KAKAO_CLIENT_SECRET
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(KAKAO_TOKEN_URL, data=payload, headers=headers)

    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="카카오 토큰 요청 실패")

    token_data = res.json()
    access_token = token_data["access_token"]

    query = urlencode({"access_token": access_token})
    return RedirectResponse(url=f"/user/login/kakao?{query}")
