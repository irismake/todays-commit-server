from .connection import SessionLocal
from ggg.models import Coord, Map

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
        ]
        for m in maps:
            db.add(Map(**m))
        db.commit()
        print("✅ map 데이터 삽입 완료", flush=True)

    except Exception as e:
        db.rollback()
        print("❌ map 삽입 실패:", e, flush=True)


def initialize_db():
    db = SessionLocal()
    try:
        if not db.query(Coord).first():
            insert_coord(db)
        if not db.query(Map).first():
            insert_map(db)
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
