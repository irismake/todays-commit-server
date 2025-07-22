import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from todays_commit.database import get_db
from todays_commit.schemas.location import LocationResponse


router = APIRouter(
    prefix="/location",
    tags=["location"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

SK_REVERSE_GEO_URL = "https://apis.openapi.sk.com/tmap/geo/reversegeocoding"
SK_APP_KEY = os.getenv("SK_APP_KEY")

def make_pnu_code(legal_dong_code:str, bunji: str) -> str:
    parts = bunji.split("-")
    main_bun = parts[0].zfill(4) if len(parts) > 0 else "0000"
    sub_bun = parts[1].zfill(4) if len(parts) > 1 else "0000"

    return legal_dong_code + "1" + main_bun + sub_bun


@router.get("/", response_model=LocationResponse)
async def get_pnu(
    lat: float = Query(...),
    lon: float = Query(...),
    db: Session = Depends(get_db)
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

    return LocationResponse(
        lat=lat,
        lon=lon,
        pnu=int(pnu)
)