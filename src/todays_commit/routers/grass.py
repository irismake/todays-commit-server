from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, UTC

from todays_commit.database import get_db
from todays_commit.models import Grass, Commit, Unit, Place
from todays_commit.schemas.oauth import auth_check
from todays_commit.schemas.grass import GrassResponse, GrassData, PostResponse


router = APIRouter(
    prefix="/grass",
    tags=["grass"],
    responses={404: {"description": "Not found"}},
)

@router.post("/{pnu}", response_model=PostResponse, dependencies=[Depends(auth_check)])
async def add_grass(
    pnu: int,
    user_id: int = Depends(auth_check),
    db: Session = Depends(get_db)
):
    place = db.query(Place).filter(Place.pnu == pnu).first()
    if not place:
        raise HTTPException(status_code=400, detail="place 정보가 없습니다. 먼저 /place API로 등록하세요.")

    
    pnu_str = str(pnu)
    unit_19 = db.query(Unit).filter(Unit.unit_code == pnu).first()

    unit_8 = db.query(Unit).filter(Unit.unit_code == int(pnu_str[:8])).first()
    if not unit_8:
        raise HTTPException(status_code=404, detail="해당하는 8자리 unit_code가 존재하지 않습니다.")

    unit_5 = db.query(Unit).filter(Unit.unit_code == int(pnu_str[:5])).first()
    if not unit_5:
        raise HTTPException(status_code=404, detail="해당하는 5자리 unit_code가 존재하지 않습니다.")

    commit = Commit(
        pnu=pnu,
        user_id=user_id,
        created_at=datetime.now(UTC)
    )
    db.add(commit)
    db.commit()
    db.refresh(commit)

    units_to_add = [u for u in [unit_19, unit_8, unit_5] if u is not None]

    for u in units_to_add:
        grass = Grass(
            map_id=u.map_id,
            coord_id=u.coord_id,
            commit_id=commit.commit_id
        )
        db.add(grass)

    db.commit()

    return PostResponse(
        message = "Success",
    )

@router.get("", response_model=GrassResponse)
async def get_grass(map_id: int = Query(...), db: Session = Depends(get_db)):
    rows = (
        db.query(Grass.coord_id, func.count().label("commit_count"))
        .filter(Grass.map_id == map_id)
        .group_by(Grass.coord_id)
        .all()
    )
    
    grass_data = [
        GrassData(coord_id=row.coord_id, commit_count=row.commit_count)
        for row in rows
    ]

    return GrassResponse(map_id=map_id, grass_data=grass_data)

@router.get("/mygrass", response_model=GrassResponse,  dependencies=[Depends(auth_check)])
async def get_my_grass(
    user_id: int = Depends(auth_check),
    map_id: int = Query(...), 
    db: Session = Depends(get_db)
):
    rows = (
        db.query(Grass.coord_id, func.count().label("commit_count"))
        .join(Commit, Grass.commit_id == Commit.commit_id)
        .filter(
            Grass.map_id == map_id,
            Commit.user_id == user_id
        )
        .group_by(Grass.coord_id)
        .all()
    )

    grass_data = [
        GrassData(coord_id=row.coord_id, commit_count=row.commit_count)
        for row in rows
    ]

    return GrassResponse(map_id=map_id, grass_data=grass_data)