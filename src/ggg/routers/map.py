from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ggg.database import get_db
from ggg.models import Map
from ggg.models import Cell
from ggg.schemas.map import MapResponse

router = APIRouter(
    prefix="/map",
    tags=["map"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.get("/{map_id}", response_model=MapResponse)
async def get(map_id: int, db: Session = Depends(get_db)):
    # 1. map_code 조회
    map_obj = db.query(Map).filter(Map.map_id == map_id).first()
    if not map_obj:
        raise HTTPException(status_code=404, detail="Map not found")

    # 2. 셀 조회 (coord_id, zone_code)
    cell_rows = (
        db.query(Cell.coord_id, Cell.zone_code)
        .filter(Cell.map_id == map_id)
        .all()
    )

    if not cell_rows:
        raise HTTPException(status_code=404, detail="No cells found for map")

    # 3. 응답 구성
    return MapResponse(
        map_code=map_obj.map_code,
        map_data=[{"coord_id": row.coord_id, "zone_code": row.zone_code} for row in cell_rows]
    )