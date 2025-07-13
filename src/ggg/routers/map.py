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
async def get( map_id: int,db: Session = Depends(get_db)):

    # 1. map_code 조회
    map_obj = db.query(Map).filter(Map.map_id == map_id).first()
    if not map_obj:
        raise HTTPException(status_code=404, detail="Map not found")

    # 2. 셀 조회 → 클래스메서드 활용
    cell_ids = Cell.get_cells(db, map_id)

    if not cell_ids:
        raise HTTPException(status_code=404, detail="No cells found for map")

    # 3. 응답 모델 구성
    return MapResponse(
        map_code=map_obj.map_code,
        cell_ids=cell_ids
    )