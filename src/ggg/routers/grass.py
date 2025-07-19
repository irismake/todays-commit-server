from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ggg.database import get_db
from ggg.models import Grass, Commit
from ggg.schemas.oauth import auth_check
from ggg.schemas.grass import GrassResponse, GrassData


router = APIRouter(
    prefix="/grass",
    tags=["grass"],
    dependencies=[Depends(auth_check)],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=GrassResponse)
async def get_grass(map_id: int = Query(...), db: Session = Depends(get_db)):
    rows = (
        db.query(Grass.coord_id, func.count().label("commit_count"))
        .filter(Grass.map_id == map_id)
        .group_by(Grass.coord_id)
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail=f"No grass data found for map_id {map_id}")

    grass_data = [
        GrassData(coord_id=row.coord_id, commit_count=row.commit_count)
        for row in rows
    ]

    return GrassResponse(map_id=map_id, grass_data=grass_data)

@router.get("/mygrass", response_model=GrassResponse)
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