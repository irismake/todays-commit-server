from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import cast, String, func


from todays_commit.database import get_db
from todays_commit.models import Map, Cell, Unit

from todays_commit.schemas.map import MapResponse, CellResponse, CellData

router = APIRouter(
    prefix="/map",
    tags=["map"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.get("/cell", response_model=list[CellResponse])
async def get_cell(pnu: int = Query(...), db: Session = Depends(get_db)):
    pnu_str = str(pnu).zfill(19)

    levels = [
        (0, int(pnu_str)),
        (1, int(pnu_str[:8])),
        (2, int(pnu_str[:5]))
    ]

    cells: list[CellResponse] = []

    for level, unit_code in levels:
        unit = db.query(Unit).filter(Unit.unit_code == unit_code).first()

        if level != 0 and not unit:
             raise HTTPException(status_code=404, detail="No matching cell by PNU")


        # level=0 & 매칭 실패 시 유사한 pnu 검색
        if level == 0 and not unit :
            print(f"⚠️ No exact match for {pnu_str}, trying similar PNU...", flush=True)
            unit = (
                db.query(Unit)
                .filter(cast(Unit.unit_code, String).like(f"{pnu_str[:15]}%"))
                .order_by(func.abs(Unit.unit_code - int(pnu_str)))  # 가장 가까운 값
                .first()
            )

            if not unit:
                continue

        cell = (
            db.query(Cell)
            .filter(Cell.map_id == unit.map_id, Cell.coord_id == unit.coord_id)
            .first()
        )
        if not cell:
            raise HTTPException(status_code=404, detail="No cells found for map")

        cells.append(
            CellResponse(
                map_level=level,
                map_id=unit.map_id,
                cell_data =CellData(
                    coord_id=unit.coord_id,
                    zone_code=cell.zone_code,
                )
            )
        )

    if not cells:
        raise HTTPException(status_code=404, detail="No mapping found for given PNU")

    return cells



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
