from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict
from enum import Enum
from math import radians, sin, cos, sqrt, atan2


from todays_commit.database import get_db
from todays_commit.models import Place, Grass, Commit, User, Unit
from todays_commit.schemas.oauth import auth_check
from todays_commit.schemas.place import PlaceBase, PlaceData, PlaceResponse, PlaceDetailResponse, PlaceCheck
from todays_commit.schemas.grass import CommitData


router = APIRouter(
    prefix="/place",
    tags=["place"],
    responses={404: {"description": "Not found"}},
)

class SortOption(str, Enum):
    recent = "recent"
    popular = "popular"



def get_distance(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance_m = R * c * 1000

    if distance_m >= 10_000:
        return "10km+"
    elif distance_m >= 1000:
        return f"{distance_m / 1000:.1f}km"
    else:
        return f"{int(round(distance_m))}m"


@router.post("", response_model=PlaceBase, dependencies=[Depends(auth_check)])
async def add_place(
    place_req: PlaceBase,
    user_id: int = Depends(auth_check),
    db: Session = Depends(get_db)
):
    if db.query(Place).filter(Place.pnu == place_req.pnu).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 장소입니다.")
    
    place = Place(**place_req.model_dump())
    db.add(place)
    db.commit()
    db.refresh(place)
    return place

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
        raise HTTPException(status_code=404, detail="No commit details found for those commit_ids")

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
    if not places:
        raise HTTPException(status_code=404, detail="No place information found for the given PNUs")

    result = []
    for place in places:
        stats = pnu_stats.get(place.pnu)
        dist = get_distance(place.x, place.y, x, y)
        result.append(PlaceData(
            pnu=place.pnu,
            name=place.name,
            distance=dist,
            commit_count=stats["count"]
        ))

    # 5. 정렬 및 limit
    if sort == SortOption.popular:
        result.sort(key=lambda x: x.commit_count, reverse=True)
    else:
        result.sort(key=lambda x: pnu_stats[x.pnu]["latest"], reverse=True)

    return PlaceResponse(places=result[:limit])

@router.get("/exist", response_model=PlaceCheck, dependencies=[Depends(auth_check)])
async def check_place(
    pnu: int = Query(...),
    db: Session = Depends(get_db)
):
     # 1. unit 테이블에서 pnu 존재 여부 확인
    unit_exists = db.query(Unit).filter(Unit.unit_code == pnu).first() is not None

    # unit 없으면 바로 exists=False 리턴
    if not unit_exists:
        return PlaceCheck(exists=False, name=None)

    # 2. place 테이블에서 pnu 존재 여부 + name 조회
    place = db.query(Place).filter(Place.pnu == pnu).first()
    place_name = place.name if place else None

    return PlaceCheck(exists=True, name=place_name)

@router.get("/myplace", response_model=PlaceResponse, dependencies=[Depends(auth_check)])
async def get_my_places(
    user_id: int = Depends(auth_check),
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
        Commit.commit_id.in_(commit_ids),
        Commit.user_id == user_id 
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
    if not places:
        raise HTTPException(status_code=404, detail="No place information found for the given PNUs")

    result = []
    for place in places:
        stats = pnu_stats.get(place.pnu)
        dist = get_distance(place.x, place.y, x, y)
        result.append(PlaceData(
            pnu=place.pnu,
            name=place.name,
            distance=dist,
            commit_count=stats["count"]
        ))

    # 5. 정렬 및 limit
    if sort == SortOption.popular:
        result.sort(key=lambda x: x.commit_count, reverse=True)
    else:
        result.sort(key=lambda x: pnu_stats[x.pnu]["latest"], reverse=True)

    return PlaceResponse(places=result[:limit])


@router.get("/{pnu}", response_model=PlaceDetailResponse)
async def get_place_detail(pnu: int, db: Session = Depends(get_db)
):
    place = db.query(Place).filter(Place.pnu == pnu).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    rows = (
        db.query(Commit.commit_id, User.user_name.label("user_name"), Commit.created_at)
        .join(User, User.user_id == Commit.user_id)
        .filter(Commit.pnu == pnu)
        .order_by(Commit.created_at.desc())
        .all()
    )

    commit_data = [
        CommitData(commit_id=row.commit_id,user_name=row.user_name, created_at=row.created_at)
        for row in rows
    ]

    return PlaceDetailResponse(
        pnu=place.pnu,
        name=place.name,
        address=place.address,
        x=place.x,
        y=place.y,
        commits= commit_data
    )
