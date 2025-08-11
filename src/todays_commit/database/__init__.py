import glob
import os
import csv
import ast
import json

from .connection import SessionLocal
from todays_commit.models import Coord, Map, Cell, Unit, Grass, Commit, User, Place, Token

def insert_mock_data(db):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    json_path = os.path.join(DATA_DIR, "mock_data.json")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        token_data = data["tokens"]
        user_data = data["users"]
        commit_data = data["commits"]
        grass_data = data["grass"]
        place_data = data["places"]
        
        # Place 테이블 삽입
        place_objs = [
            Place(
                pnu= item["pnu"],
                name= item["name"],
                address= item["address"],
                x= item["x"],
                y= item["y"],
            )
            for item in place_data
        ]
        db.add_all(place_objs)
        db.commit()

         # User 테이블 삽입
        user_objs = [
            User(
                user_id= item["user_id"],
                user_name = item["user_name"],
                email = item["email"],
                provider= item["provider"],
                provider_id= item["provider_id"],
                created_at= item["created_at"],
            )
            for item in user_data
        ]
        db.add_all(user_objs)
        db.commit()

        # Token 테이블 삽입
        token_objs = [
            Token(
                user_id= item["user_id"],
                refresh_token= item["refresh_token"],
                created_at= item["created_at"],
                expires_at= item["expires_at"],
            )
            for item in token_data
        ]
        db.add_all(token_objs)
        db.commit()

        # Commit 테이블 삽입
        commit_objs = [
            Commit(
                commit_id=item["commit_id"],
                pnu=item["pnu"],
                user_id=item["user_id"],
                created_at=item["created_at"]
            )
            for item in commit_data
        ]
        db.add_all(commit_objs)
        db.commit()

        # Grass 테이블 삽입
        grass_objs = [
            Grass(
                grass_id=item["grass_id"],
                commit_id=item["commit_id"],
                coord_id=item["coord_id"],
                map_id=item["map_id"]
            )
            for item in grass_data
        ]
        db.add_all(grass_objs)
        db.commit()
        print("✅ mock data 삽입 완료", flush=True)
    except Exception as e:
        db.rollback()
        print(f"❌ mock data 삽입 실패: {e}", flush=True)


def insert_coord(db):
    try:
        coord_id = 0
        for y in range(25):
            for x in range(25):
                db.add(Coord(coord_id=coord_id, x=x, y=y))
                coord_id += 1
        db.commit()
        print("✅ coord 좌표 삽입 완료", flush=True)
    except Exception as e:
        db.rollback()
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
            {"map_id": 19, "map_level": 0, "map_code": 11305},
            {"map_id": 20, "map_level": 0, "map_code": 11290},
        ]
        for m in maps:
            db.add(Map(**m))
        db.commit()
        print("✅ map 데이터 삽입 완료", flush=True)

    except Exception as e:
        db.rollback()
        print("❌ map 삽입 실패:", e, flush=True)


def insert_csv(db):
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
            inserted_cells = 0
            inserted_units = 0

            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader, None)
                
                print(f"📌 파일: {filename}, 헤더: {headers}")

                if headers != ["y", "x", "zone_code", "pnus"]:
                    raise ValueError(f"❌ 잘못된 헤더입니다. 파일: {filename}, 헤더: {headers}")

                for line_no, row in enumerate(reader, start=2):
                    try:
                        if len(row) != 4:
                            raise ValueError(f"데이터 필드 에러: {filename}")
                        y = int(row[0])
                        x = int(row[1])
                        zone_code = int(row[2])
                        pnus_raw = row[3]

                        coord = db.query(Coord).filter_by(x=x, y=y).first()
                        if not coord:
                            raise ValueError(f"⚠️ coord({x},{y}) 없음 (파일: {filename}, 줄: {line_no})")

                        exists = db.query(Cell).filter_by(coord_id=coord.coord_id, map_id=map_id).first()
                        if exists:
                            raise ValueError(f"⚠️ 중복 Cell 존재: coord_id={coord.coord_id}, map_id={map_id} (파일: {filename}, 줄: {line_no})")

                        db.add(Cell(coord_id=coord.coord_id, map_id=map_id, zone_code=zone_code))
                        inserted_cells += 1

                        if pnus_raw:
                            try:
                                pnus = ast.literal_eval(pnus_raw)
                                if not isinstance(pnus, list):
                                    raise ValueError("⚠️ pnus가 리스트가 아닙니다")
                                for unit_code in pnus:
                                    db.add(Unit(coord_id=coord.coord_id, map_id=map_id, unit_code=unit_code))
                                    inserted_units += 1
                            except Exception as pe:
                                raise ValueError(f"⚠️ pnus 파싱 오류 (파일: {filename}, 줄: {line_no}, 값: {pnus_raw}) → {pe}")

                    except Exception as row_error:
                        raise ValueError(f"⚠️ row 처리 중 에러 (파일: {filename}, 줄: {line_no}) → {row_error}")

            db.commit()
            print(f"✅ {filename} → cell {inserted_cells}개, unit {inserted_units}개 삽입 완료", flush=True)

    except Exception as e:
        db.rollback()
        print(f"❌ 처리 중 오류 발생: {e}", flush=True)
        raise


def initialize_db():
    db = SessionLocal()
    reset_table(db)
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
        if not db.query(Cell).first() or not db.query(Unit).first():
            print("🚀 insert_csv 실행", flush=True)
            insert_csv(db)
        else:
            print("✅ Cell & Unit 데이터 있음",  flush=True)
        if not db.query(Commit).first():
            print("🚀 insert_mock_data 실행", flush=True)
            insert_mock_data(db)
        else:
            print("✅ Mock 데이터 있음",  flush=True)
    finally:
        db.close()


def reset_table(db):
    try:
        db.query(Grass).delete()
        db.query(Commit).delete()
        db.query(Unit).delete()
        db.query(Cell).delete()
        db.query(Map).delete()
        db.query(Token).delete()
        db.query(User).delete()
        db.query(Place).delete()
        db.query(Coord).delete()
        db.commit()
        print(f"🧹 테이블 초기화 완료",  flush=True)
    except Exception as e:
        db.rollback()
        print(f"❌ 테이블 초기화 실패: {e}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
