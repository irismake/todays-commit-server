from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, and_
from typing import Optional
from enum import Enum
from datetime import datetime
import base64
import json

from todays_commit.database import get_db
from todays_commit.models import Place, Grass, Commit, User, Unit
from todays_commit.schemas.oauth import auth_check
from todays_commit.schemas.place import PlaceBase, PlaceData, PlaceResponse, PlaceDetailResponse, PlaceCheck
from todays_commit.schemas.commit import CommitData
from todays_commit.schemas.base import PostResponse


router = APIRouter(
    prefix="/place",
    tags=["place"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class SortOption(str, Enum):
    recent = "recent"
    popular = "popular"

def encode_cursor(data: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

def decode_cursor(cursor: str) -> dict:
    return json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())


@router.post("", response_model=PostResponse, dependencies=[Depends(auth_check)])
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

    return PostResponse(
        message = "Success",
    )


@router.get("/exist", response_model=PlaceCheck, dependencies=[Depends(auth_check)])
async def check_place(
    pnu: int = Query(...),
    db: Session = Depends(get_db)
):
    unit = db.query(Unit).filter(Unit.unit_code == pnu).first()
    place = db.query(Place).filter(Place.pnu == pnu).first()

    if unit:  
        return PlaceCheck(
            exists=True,
            name=place.name if place else None
        )

    if place:
        return PlaceCheck(
            exists=False,
            name=place.name
        )

    return PlaceCheck(exists=False, name=None)


@router.get("/main", response_model=PlaceResponse)
async def get_places(
    map_id: int = Query(...),
    coord_id: int = Query(...),
    sort: SortOption = Query(SortOption.recent),
    cursor: Optional[str] = Query(None, description="다음 페이지 커서 값"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # 1. pnu별 commit_count, latest_commit_at 서브쿼리
    commit_stats_subquery = db.query(
        Commit.pnu,
        func.count(Commit.commit_id).label("commit_count"),
        func.max(Commit.created_at).label("latest_commit_at")
    ).filter(
        Commit.commit_id.in_(
            db.query(Grass.commit_id).filter(
                Grass.map_id == map_id,
                Grass.coord_id == coord_id
            )
        )
    ).group_by(Commit.pnu).subquery()
    
    # 2. 메인 쿼리
    query = db.query(
        Place.pnu,
        Place.name,
        Place.address,  # address 추가
        Place.x,
        Place.y,
        commit_stats_subquery.c.commit_count,
        commit_stats_subquery.c.latest_commit_at
    ).join(
        commit_stats_subquery,
        Place.pnu == commit_stats_subquery.c.pnu
    )
    
    # 3. 커서 기반 필터링
    if cursor:
        try:
            cursor_data = decode_cursor(cursor)

            if sort == SortOption.popular:
                cursor_count = cursor_data["count"]
                cursor_pnu = cursor_data["pnu"]

                query = query.filter(
                    or_(
                        commit_stats_subquery.c.commit_count < cursor_count,
                        and_(
                            commit_stats_subquery.c.commit_count == cursor_count,
                            Place.pnu < cursor_pnu
                        )
                    )
                )
            else:  # SortOption.recent
                cursor_dt = datetime.fromisoformat(cursor_data["dt"])
                cursor_pnu = cursor_data["pnu"]

                query = query.filter(
                    or_(
                        commit_stats_subquery.c.latest_commit_at < cursor_dt,
                        and_(
                            commit_stats_subquery.c.latest_commit_at == cursor_dt,
                            Place.pnu < cursor_pnu
                        )
                    )
                )
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid cursor value")
    
    # 4. 정렬
    if sort == SortOption.popular:
        query = query.order_by(
            desc(commit_stats_subquery.c.commit_count),
            desc(Place.pnu)
        )
    else:
        query = query.order_by(
            desc(commit_stats_subquery.c.latest_commit_at),
            desc(Place.pnu)
        )
    
    # 5. limit+1
    results = query.limit(limit + 1).all()

    if not results:
        return PlaceResponse(places=[], next_cursor=None)

    # 6. 결과 처리
    places_data = [
        PlaceData(
            pnu=r.pnu,
            name=r.name,
            address=r.address,
            x=r.x,
            y=r.y,
            commit_count=r.commit_count
        )
        for r in results[:limit]
    ]

    # 7. next_cursor
    next_cursor = None
    if len(results) > limit:
        last_item = results[limit - 1]
        if sort == SortOption.popular:
            next_cursor = encode_cursor({
                "count": last_item.commit_count,
                "pnu": last_item.pnu
            })
        else:
            next_cursor = encode_cursor({
                "dt": last_item.latest_commit_at.isoformat(),
                "pnu": last_item.pnu
            })

    return PlaceResponse(places=places_data, next_cursor=next_cursor)


@router.get("/myplace", response_model=PlaceResponse, dependencies=[Depends(auth_check)])
async def get_my_places(
    user_id: int = Depends(auth_check),
    map_id: int = Query(...),
    coord_id: int = Query(...),
    sort: SortOption = Query(SortOption.recent),
    cursor: Optional[str] = Query(None, description="다음 페이지 커서 값"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # 1. pnu별 commit_count, latest_commit_at 서브쿼리
    commit_stats_subquery = db.query(
        Commit.pnu,
        func.count(Commit.commit_id).label("commit_count"),
        func.max(Commit.created_at).label("latest_commit_at")
    ).filter(
        Commit.commit_id.in_(
            db.query(Grass.commit_id).filter(
                Grass.map_id == map_id,
                Grass.coord_id == coord_id
            )
        ),
        Commit.user_id == user_id
    ).group_by(Commit.pnu).subquery()

    # 2. 메인 쿼리
    query = db.query(
        Place.pnu,
        Place.name,
        Place.address,
        Place.x,
        Place.y,
        commit_stats_subquery.c.commit_count,
        commit_stats_subquery.c.latest_commit_at
    ).join(
        commit_stats_subquery,
        Place.pnu == commit_stats_subquery.c.pnu
    )

    # 3. 커서 필터링
    if cursor:
        try:
            cursor_data = decode_cursor(cursor)
            if sort == SortOption.popular:
                cursor_count = cursor_data["count"]
                cursor_pnu = cursor_data["pnu"]
                query = query.filter(
                    or_(
                        commit_stats_subquery.c.commit_count < cursor_count,
                        and_(
                            commit_stats_subquery.c.commit_count == cursor_count,
                            Place.pnu < cursor_pnu
                        )
                    )
                )
            else:
                cursor_dt = datetime.fromisoformat(cursor_data["dt"])
                cursor_pnu = cursor_data["pnu"]
                query = query.filter(
                    or_(
                        commit_stats_subquery.c.latest_commit_at < cursor_dt,
                        and_(
                            commit_stats_subquery.c.latest_commit_at == cursor_dt,
                            Place.pnu < cursor_pnu
                        )
                    )
                )
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid cursor value")

    # 4. 정렬
    if sort == SortOption.popular:
        query = query.order_by(
            desc(commit_stats_subquery.c.commit_count),
            desc(Place.pnu)
        )
    else:
        query = query.order_by(
            desc(commit_stats_subquery.c.latest_commit_at),
            desc(Place.pnu)
        )

    # 5. limit+1
    results = query.limit(limit + 1).all()

    if not results:
        return PlaceResponse(places=[], next_cursor=None)

    # 6. 데이터 변환
    places_data = [
        PlaceData(
            pnu=r.pnu,
            name=r.name,
            address=r.address,
            x=r.x,
            y=r.y,
            commit_count=r.commit_count
        )
        for r in results[:limit]
    ]

    # 7. next_cursor
    next_cursor = None
    if len(results) > limit:
        last_item = results[limit - 1]
        if sort == SortOption.popular:
            next_cursor = encode_cursor({
                "count": last_item.commit_count,
                "pnu": last_item.pnu
            })
        else:
            next_cursor = encode_cursor({
                "dt": last_item.latest_commit_at.isoformat(),
                "pnu": last_item.pnu
            })

    return PlaceResponse(places=places_data, next_cursor=next_cursor)


@router.get("/myplaces", response_model=PlaceResponse, dependencies=[Depends(auth_check)])
async def get_my_places(
    user_id: int = Depends(auth_check),
    cursor: Optional[str] = Query(None, description="다음 페이지 커서 값"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # 1. commit 테이블에서 user_id별 커밋 가져오기 + pnu 그룹화
    commit_counts = (
        db.query(
            Commit.pnu,
            func.count(Commit.commit_id).label("commit_count")
        )
        .filter(Commit.user_id == user_id)
        .group_by(Commit.pnu)
        .subquery()
    )

    # 2. place 테이블과 join
    query = (
        db.query(
            Place.pnu,
            Place.name,
            Place.address,
            Place.x,
            Place.y,
            commit_counts.c.commit_count
        )
        .join(commit_counts, Place.pnu == commit_counts.c.pnu)
    )

    # 3. 커서 기반 필터링 (인기순: commit_count → pnu)
    if cursor:
        try:
            cursor_data = decode_cursor(cursor)
            cursor_count = cursor_data["count"]
            cursor_pnu = cursor_data["pnu"]

            query = query.filter(
                or_(
                    commit_counts.c.commit_count < cursor_count,
                    and_(
                        commit_counts.c.commit_count == cursor_count,
                        Place.pnu < cursor_pnu
                    )
                )
            )
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid cursor value")

    # 4. 정렬 (인기순)
    query = query.order_by(
        desc(commit_counts.c.commit_count),
        desc(Place.pnu)
    )

    # 5. limit+1
    results = query.limit(limit + 1).all()

    if not results:
        return PlaceResponse(places=[], next_cursor=None)

    # 6. 결과 변환
    places = [
        PlaceData(
            pnu=r.pnu,
            name=r.name,
            address=r.address,
            x=r.x,
            y=r.y,
            commit_count=r.commit_count
        )
        for r in results[:limit]
    ]

    # 7. next_cursor 생성
    next_cursor = None
    if len(results) > limit:
        last_item = results[limit - 1]
        next_cursor = encode_cursor({
            "count": last_item.commit_count,
            "pnu": last_item.pnu
        })

    return PlaceResponse(places=places, next_cursor=next_cursor)


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
