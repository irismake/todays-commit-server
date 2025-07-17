from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict
from enum import Enum
from math import radians, cos, sin, asin, sqrt

from ggg.database import get_db
from ggg.models import Place, Grass, Commit
from ggg.schemas.place import PlaceData, PlaceResponse

router = APIRouter(
    prefix="/place",
    tags=["place"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class SortOption(str, Enum):
    recent = "recent"
    popular = "popular"


def get_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return round(R * c * 1000)


@router.get("/main", response_model=PlaceResponse)
async def get_places(
    map_id: int = Query(...),
    coord_id: int= Query(...),
    x: float = Query(...),
    y: float = Query(...),
    sort: SortOption = Query(SortOption.recent),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # 1. grass → commit_id 목록
    commit_ids = db.query(Grass.commit_id).filter(
        Grass.map_id == map_id,
        Grass.coord_id == coord_id
    ).all()
    commit_ids = [cid[0] for cid in commit_ids]
    if not commit_ids:
        return PlaceResponse(places=[])

    # 2. commit → pnu, created_at 목록
    commits = db.query(Commit.pnu, Commit.created_at).filter(
        Commit.commit_id.in_(commit_ids)
    ).all()

    if not commits:
        return PlaceResponse(places=[])

    # 3. pnu → commit_count, 최근 시간
    pnu_stats: Dict[int, Dict] = {}
    for pnu, created_at in commits:
        if pnu not in pnu_stats:
            pnu_stats[pnu] = {"count": 0, "latest": created_at}
        pnu_stats[pnu]["count"] += 1
        if created_at > pnu_stats[pnu]["latest"]:
            pnu_stats[pnu]["latest"] = created_at

    # 4. place 테이블에서 정보 가져오기
    places = db.query(Place).filter(Place.pnu.in_(pnu_stats.keys())).all()

    result = []
    for place in places:
        stats = pnu_stats.get(place.pnu)
        dist = get_distance(place.y, place.x, x, y)
        result.append(PlaceData(
            pnu=place.pnu,
            name=place.name,
            distance=round(dist, 2),
            commit_count=stats["count"]
        ))

    # 5. 정렬 및 limit
    if sort == SortOption.popular:
        result.sort(key=lambda x: x.commit_count, reverse=True)
    else:
        result.sort(key=lambda x: pnu_stats[x.pnu]["latest"], reverse=True)

    return PlaceResponse(
        places=result[:limit]
    )