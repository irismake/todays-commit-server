import os
import re
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from todays_commit.database import get_db
from todays_commit.schemas.location import LocationResponse, SearchLocationData


router = APIRouter(
    prefix="/location",
    tags=["location"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

SK_REVERSE_GEO_URL = "https://apis.openapi.sk.com/tmap/geo/reversegeocoding"
SK_APP_KEY = os.getenv("SK_APP_KEY")

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"


def make_pnu_code(legal_dong_code: str, bunji: str) -> str:
    is_san = "산" in bunji
    # 숫자와 '-'만 남기기
    clean_bunji = re.sub(r"[^0-9\-]", "", bunji)
    parts = clean_bunji.split("-")
    # 본번 / 부번
    main_bun = parts[0].zfill(4) if len(parts) > 0 and parts[0] else "0000"
    sub_bun  = parts[1].zfill(4) if len(parts) > 1 and parts[1] else "0000"
    san_code = "2" if is_san else "1"
    return legal_dong_code + san_code + main_bun + sub_bun

@router.get("", response_model=LocationResponse)
async def get_pnu(
    lat: float = Query(...),
    lon: float = Query(...),
    # db: Session = Depends(get_db)
):
    headers = {
        "appKey": SK_APP_KEY
    }

    params = {
        "version":1,
        "addressType":"A02",
        "lat": str(lat),
        "lon": str(lon),
        "newAddressExtend":"Y"
    }
    
    async with httpx.AsyncClient() as client:
        res = await client.get(SK_REVERSE_GEO_URL, headers=headers, params=params)
    if res.status_code != 200:
        raise HTTPException(status_code=502, detail="SK Open API 호출 실패")
    res_data = res.json()
    address_info = res_data.get("addressInfo")
    if not address_info:
        raise HTTPException(status_code=404, detail="좌표에 해당하는 행정구역이 없습니다.")
    # fullAddress = address_info("fullAddress")
    # ri = address_info("ri")
    pnu = make_pnu_code(address_info.get("legalDongCode"), address_info.get("bunji"))
    address = address_info.get("fullAddress")
    return LocationResponse(
        lat=lat,
        lon=lon,
        pnu=int(pnu),
        address=address
    )


@router.get("/search", response_model=list[SearchLocationData])
async def search_location(
    query: str = Query(..., description="검색할 키워드"),
    x: Optional[float] = Query(None, description="중심 좌표 X (경도)"),
    y: Optional[float] = Query(None, description="중심 좌표 Y (위도)"),
    radius: Optional[int] = Query(2000, description="검색 반경 (m)"),
    sort: Optional[str] = Query("accuracy", description="정렬 방식: accuracy | distance"),
    # db: Session = Depends(get_db)
):
    if not KAKAO_REST_API_KEY:
        raise HTTPException(status_code=500, detail="KAKAO_REST_API_KEY 환경변수 미설정")

    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }

    params = {
        "query": query,
        "radius": radius,
        "sort": sort
    }
    if x and y:
        params["x"] = x
        params["y"] = y

    async with httpx.AsyncClient() as client:
        res = await client.get(KAKAO_SEARCH_URL, headers=headers, params=params)

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail="카카오 장소 검색 실패")

    data = res.json()
    documents = data.get("documents", [])

    return [
        SearchLocationData(
            place_name=doc.get("place_name"),
            address_name=doc.get("address_name"),
            road_address_name=doc.get("road_address_name"),
            x=doc.get("x"),
            y=doc.get("y"),
            distance=doc.get("distance")
        )
        for doc in documents
    ]
