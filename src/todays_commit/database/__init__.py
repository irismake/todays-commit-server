import glob
import os
import csv
import ast
import json

from .connection import SessionLocal
from todays_commit.models import Coord, Map, Cell, Unit

def insert_coord(db):
    try:
        coord_id = 0
        for y in range(22):
            for x in range(22):
                db.add(Coord(coord_id=coord_id, x=x, y=y))
                coord_id += 1
        db.commit()
        print("✅ coord 좌표 삽입 완료", flush=True)
    except Exception as e:
        db.rollback()
        print("❌ coord 삽입 실패:", e, flush=True)


def insert_map(db):
    maps = [
        {"map_id": 1, "map_level": 2, "map_code": 410},
        {"map_id": 2, "map_level": 1, "map_code": 51},
        {"map_id": 3, "map_level": 1, "map_code": 41},
        {"map_id": 4, "map_level": 1, "map_code": 48},
        {"map_id": 5, "map_level": 1, "map_code": 47},
        {"map_id": 6, "map_level": 1, "map_code": 29},
        {"map_id": 7, "map_level": 1, "map_code": 27},
        {"map_id": 8, "map_level": 1, "map_code": 30},
        {"map_id": 9, "map_level": 1, "map_code": 26},
        {"map_id": 10, "map_level": 1, "map_code": 11},
        {"map_id": 11, "map_level": 1, "map_code": 36},
        {"map_id": 12, "map_level": 1, "map_code": 31},
        {"map_id": 13, "map_level": 1, "map_code": 28},
        {"map_id": 14, "map_level": 1, "map_code": 46},
        {"map_id": 15, "map_level": 1, "map_code": 52},
        {"map_id": 16, "map_level": 1, "map_code": 50},
        {"map_id": 17, "map_level": 1, "map_code": 44},
        {"map_id": 18, "map_level": 1, "map_code": 43},
        {"map_id": 19, "map_level": 0, "map_code": 11110},
        {"map_id": 20, "map_level": 0, "map_code": 11140},
        {"map_id": 21, "map_level": 0, "map_code": 11170},
        {"map_id": 22, "map_level": 0, "map_code": 11200},
        {"map_id": 23, "map_level": 0, "map_code": 11215},
        {"map_id": 24, "map_level": 0, "map_code": 11230},
        {"map_id": 25, "map_level": 0, "map_code": 11260},
        {"map_id": 26, "map_level": 0, "map_code": 11290},
        {"map_id": 27, "map_level": 0, "map_code": 11305},
        {"map_id": 28, "map_level": 0, "map_code": 11320},
        {"map_id": 29, "map_level": 0, "map_code": 11350},
        {"map_id": 30, "map_level": 0, "map_code": 11380},
        {"map_id": 31, "map_level": 0, "map_code": 11410},
        {"map_id": 32, "map_level": 0, "map_code": 11440},
        {"map_id": 33, "map_level": 0, "map_code": 11470},
        {"map_id": 34, "map_level": 0, "map_code": 11500},
        {"map_id": 35, "map_level": 0, "map_code": 11530},
        {"map_id": 36, "map_level": 0, "map_code": 11545},
        {"map_id": 37, "map_level": 0, "map_code": 11560},
        {"map_id": 38, "map_level": 0, "map_code": 11590},
        {"map_id": 39, "map_level": 0, "map_code": 11620},
        {"map_id": 40, "map_level": 0, "map_code": 11650},
        {"map_id": 41, "map_level": 0, "map_code": 11680},
        {"map_id": 42, "map_level": 0, "map_code": 11710},
        {"map_id": 43, "map_level": 0, "map_code": 11740},
    ]
    new_maps = []



    for m in maps: 
        exists = db.query(Map).filter_by(map_id=m["map_id"]).first() 
        if not exists: 
            db.add(Map(**m)) 
            new_maps.append(m) 
    print(f"📝 map 추가 준비 완료 (신규 {len(new_maps)}개)") 
    return new_maps


def insert_csv(db, new_maps):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")

    for m in new_maps:
        filename = f"{m['map_code']}.csv"
        csv_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"❌ CSV 파일 없음: {filename} (map_id={m['map_id']})")

        print(f"🚀 CSV 처리 시작: {filename}", flush=True)
        inserted_cells = 0
        inserted_units = 0

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, None)
            if headers != ["y", "x", "zone_code", "pnus"]:
                raise ValueError(f"❌ 잘못된 헤더입니다. 파일: {filename}, 헤더: {headers}")

            for line_no, row in enumerate(reader, start=2):
                if len(row) != 4:
                    raise ValueError(f"데이터 필드 에러: {filename}")
                y = int(row[0])
                x = int(row[1])
                zone_code = int(row[2])
                pnus_raw = row[3]

                coord = db.query(Coord).filter_by(x=x, y=y).first()
                if not coord:
                    raise ValueError(f"⚠️ coord({x},{y}) 없음 (파일: {filename}, 줄: {line_no})")

                exists = db.query(Cell).filter_by(coord_id=coord.coord_id, map_id=m["map_id"]).first()
                if exists:
                    raise ValueError(
                        f"⚠️ 중복 Cell 존재: coord_id={coord.coord_id}, map_id={m['map_id']} "
                        f"(파일: {filename}, 줄: {line_no})"
                    )

                db.add(Cell(coord_id=coord.coord_id, map_id=m["map_id"], zone_code=zone_code))
                inserted_cells += 1

                if pnus_raw:
                    pnus = ast.literal_eval(pnus_raw)
                    if not isinstance(pnus, list):
                        raise ValueError("⚠️ pnus가 리스트가 아닙니다")
                    for unit_code in pnus:
                        db.add(Unit(coord_id=coord.coord_id, map_id=m["map_id"], unit_code=unit_code))
                        inserted_units += 1

        print(f"✅ {filename} → cell {inserted_cells}개, unit {inserted_units}개 삽입 준비 완료", flush=True)




def initialize_db():
    db = SessionLocal()
    try:
        if not db.query(Coord).first():
            print("🚀 insert_coord 실행", flush=True)
            insert_coord(db)
        else:
            print("✅ Coord 데이터 있음", flush=True)

        print("🚀 insert_map 실행", flush=True)
        new_maps = insert_map(db)
        db.flush()

        if new_maps:
            print("🚀 insert_csv 실행", flush=True)
            insert_csv(db, new_maps)

        db.commit()
        print("✅ 모든 데이터 삽입 완료", flush=True)

    except Exception as e:
        db.rollback()
        print(f"❌ 초기화 중 오류 발생: {e}", flush=True)
        raise
    finally:
        db.close()


def reset_table(db):
    try:
        db.query(Unit).delete()
        db.query(Cell).delete()
        db.query(Map).delete()
        db.query(Coord).delete()
        db.commit()
        print(f"🧹 테이블 초기화 완료",  flush=True)
    except Exception as e:
        db.rollback()
        print(f"❌ 테이블 초기화 실패: {e}", flush=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
