from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ggg.database import get_db
from ggg.models import Grass
from ggg.schemas.grass import GrassResponse, GrassData


router = APIRouter(
    prefix="/grass",
    tags=["grass"],
    dependencies=[],
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