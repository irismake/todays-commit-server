import glob
import os
import csv

from .connection import SessionLocal
from ggg.models import Coord, Map, Cell


def insert_coord(db):
    try:
        for x in range(25):
            for y in range(25):
                db.add(Coord(x=x, y=y))
        db.commit()
        print("✅ coord 좌표 삽입 완료", flush=True)
    except Exception as e:
        print("❌ coord 삽입 실패:", e, flush=True)


def insert_map(db):
    try:
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
            {"map_id": 19, "map_level": 0, "map_code": 11350},
            {"map_id": 20, "map_level": 0, "map_code": 11290},
        ]
        for m in maps:
            db.add(Map(**m))
        db.commit()
        print("✅ map 데이터 삽입 완료", flush=True)

    except Exception as e:
        db.rollback()
        print("❌ map 삽입 실패:", e, flush=True)


def insert_cell(db):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

    try:
        for csv_path in sorted(csv_files):
            filename = os.path.basename(csv_path)
            map_code = int(os.path.splitext(filename)[0])

            map_row = db.query(Map).filter_by(map_code=map_code).first()
            if not map_row:
                raise ValueError(f"⚠️ map_code {map_code}에 해당하는 map이 DB에 존재하지 않습니다.")

            map_id = map_row.map_id
            inserted = 0

            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None)

                for line_no, row in enumerate(reader, start=2):
                    if len(row) < 3:
                        raise ValueError(f"⚠️ csv 포맷 에러 (파일: {filename}, 줄: {line_no}, row: {row})")

                    y = int(row[0])
                    x = int(row[1])
                    zone_code = int(row[2])

                    coord = db.query(Coord).filter_by(x=x, y=y).first()
                    if not coord:
                        raise ValueError(f"⚠️ coord({x},{y}) 없음 (파일: {filename}, 줄: {line_no})")

                    exists = db.query(Cell).filter_by(coord_id=coord.coord_id, map_id=map_id).first()
                    if exists:
                        raise ValueError(f"⚠️ 중복 Cell 존재: coord_id={coord.coord_id}, map_id={map_id} (파일: {filename}, 줄: {line_no})")

                    db.add(Cell(coord_id=coord.coord_id, map_id=map_id, zone_code=zone_code))
                    inserted += 1

            db.commit()
            print(f"✅ {filename} → {inserted}개 cell 삽입 완료", flush=True)

    except Exception as e:
        db.rollback()
        print(f"❌ 처리 중 오류 발생: {e}", flush=True)
        raise


def initialize_db():
    db = SessionLocal()
    try:
        if not db.query(Coord).first():
            print("🚀 insert_coord 실행", flush=True)
            insert_coord(db)
        else:
            print("✅ Coord 데이터 있음", flush=True)
        if not db.query(Map).first():
            print("🚀 insert_map 실행", flush=True)
            insert_map(db)
        else:
            print("✅ Map 데이터 있음", flush=True)
        if not db.query(Cell).first():
            print("🚀 insert_cell 실행", flush=True)
            insert_cell(db)
        else:
            print("✅ Cell 데이터 있음")
    finally:
        db.close()


# def reset_cell_table(db):
#     try:
#         deleted = db.query(Cell).delete()
#         deleted = db.query(Map).delete()
#         db.commit()
#         print(f"🧹 테이블 초기화 완료 ({deleted}개 삭제됨)")
#     except Exception as e:
#         db.rollback()
#         print(f"❌ 테이블 초기화 실패: {e}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
