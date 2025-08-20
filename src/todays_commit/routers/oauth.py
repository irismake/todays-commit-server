from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
import httpx
import time
import jwt
import json
import os
from urllib.parse import urlencode

router = APIRouter(
    prefix="/oauth",
    tags=["oauth"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

# KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
# KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
# KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
# KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
# KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"

# APPLE_AUTH_URL = "https://appleid.apple.com/auth/authorize"
APPLE_TEAM_ID = os.getenv("APPLE_TEAM_ID")
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")
APPLE_KEY_ID = os.getenv("APPLE_KEY_ID")
APPLE_REDIRECT_URI = os.getenv("APPLE_REDIRECT_URI")
APPLE_PRIVATE_KEY_FILE = os.getenv("APPLE_PRIVATE_KEY_FILE")
APPLE_TOKEN_URL = "https://appleid.apple.com/auth/token"


def create_apple_client_secret():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
    DATA_DIR = os.path.join(PARENT_DIR, "database", "data")
    json_path = os.path.join(DATA_DIR, APPLE_PRIVATE_KEY_FILE)
    private_key = open(json_path).read()

    headers = {
        "kid": APPLE_KEY_ID,
    }
    claims = {
        "iss": APPLE_TEAM_ID,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "aud": "https://appleid.apple.com",
        "sub": APPLE_CLIENT_ID
    }

    apple_client_secret = jwt.encode(claims, private_key, algorithm="ES256", headers=headers)
    return apple_client_secret

#### web 용 kakao oauth 로그인

# @router.get("/kakao/url")
# async def get_kakao_login_url():
#     url = (
#         f"{KAKAO_AUTH_URL}"
#         f"?client_id={KAKAO_CLIENT_ID}"
#         f"&redirect_uri={KAKAO_REDIRECT_URI}"
#         f"&response_type=code"
#         f"&prompt=login"
#     )
#     return RedirectResponse(url)


# @router.get("/kakao/callback")
# async def kakao_callback(code: str = Query(...)):
#     payload = {
#         "grant_type": "authorization_code",
#         "client_id": KAKAO_CLIENT_ID,
#         "redirect_uri": KAKAO_REDIRECT_URI,
#         "code": code,
#         "client_secret": KAKAO_CLIENT_SECRET
#     }

#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded"
#     }

#     async with httpx.AsyncClient() as client:
#         res = await client.post(KAKAO_TOKEN_URL, data=payload, headers=headers)

#     if res.status_code != 200:
#         raise HTTPException(status_code=400, detail="카카오 토큰 요청 실패")

#     token_data = res.json()
#     access_token = token_data["access_token"]

#     query = urlencode({"access_token": access_token})
#     return RedirectResponse(url=f"/user/login/kakao?{query}")


# @router.get("/apple/url")
# async def get_apple_login_url():
#     base_url = APPLE_AUTH_URL
#     params = {
#         "response_type": "code",
#         "response_mode": "form_post",
#         "client_id": APPLE_CLIENT_ID,
#         "redirect_uri": APPLE_REDIRECT_URI,
#         "scope": "name email",
#         "state": "optional-custom-state"
#     }

#     url = f"{base_url}?{urlencode(params)}"
#     return RedirectResponse(url)


@router.post("/apple/token")
async def apple_callback(request: Request):
    form = await request.form()
    user_name = form.get("user_name")
    code = form.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="code not found")

    client_secret = create_apple_client_secret()
    token_url = APPLE_TOKEN_URL
    payload = {
        "client_id": APPLE_CLIENT_ID,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": APPLE_REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        res = await client.post(token_url, data=payload, headers=headers)

    if res.status_code != 200:
        print("status_code:", res.status_code)
        print("response body:", res.text)
        raise HTTPException(status_code=400, detail="Apple 토큰 요청 실패")

    token_data = res.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Apple access_token 없음")

    query = {"id_token": token_data["id_token"]}
    if user_name and user_name.strip():
        query["user_name"] = user_name.strip()

    return RedirectResponse(url=f"/user/login/apple?{urlencode(query)}", status_code=303)