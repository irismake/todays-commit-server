from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from todays_commit.database import get_db
from todays_commit.models import Map, Cell, Unit

from todays_commit.schemas.map import MapResponse, CellResponse, CellData

router = APIRouter(
    prefix="/map",
    tags=["map"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.get("/cell", response_model=CellResponse)
async def get_cell(pnu: int = Query(...), db: Session = Depends(get_db)):
    pnu_str = str(pnu).zfill(19)
    result_maps = []

    levels = [
        (2, int(pnu_str)),
        (1, int(pnu_str[:8])),
        (0, int(pnu_str[:5]))
    ]

    for level, unit_code in levels:
        unit = db.query(Unit).filter(Unit.unit_code == unit_code).first()
        if unit:
            result_maps.append(
                CellData(
                    map_level=level,
                    map_id=unit.map_id,
                    coord_id=unit.coord_id
                )
            )

    if not result_maps:
        raise HTTPException(status_code=404, detail="No mapping found for given PNU")

    return CellResponse(pnu=pnu, maps=result_maps)



@router.get("/{map_id}", response_model=MapResponse)
async def get_map(map_id: int, db: Session = Depends(get_db)):
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
