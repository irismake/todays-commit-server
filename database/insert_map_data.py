import sqlite3
import csv
import os
import ast

# 경로 설정
base_dir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(base_dir, "../instance")
db_path = os.path.join(base_dir, "../sqlite_data/ggg.db")

# DB 연결
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

map_id_counter = 1
subzone_inserts = []

# 디렉토리 내 모든 CSV 파일 순회
for filename in os.listdir(instance_dir):
    if filename.endswith(".csv"):
        csv_path = os.path.join(instance_dir, filename)

        try:
            map_code = int(os.path.splitext(filename)[0])  # 파일명에서 숫자 추출
        except ValueError:
            print(f"⚠️  파일 이름이 숫자가 아님: {filename} → 건너뜀")
            continue

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                x = int(row["x"])
                y = int(row["y"])
                zone_code = int(row["zone_code"])

                # map 테이블에 삽입
                cursor.execute(
                    "INSERT INTO map (map_id, map_code, zone_code, x, y) VALUES (?, ?, ?, ?, ?)",
                    (map_id_counter, map_code, zone_code, x, y)
                )

                # sub_zone_codes 파싱해서 subzone 테이블용 데이터 준비
                raw = row.get("sub_zone_codes", "").strip()
                if raw:
                    try:
                        codes = ast.literal_eval(raw)
                        if isinstance(codes, list):
                            for code in codes:
                                subzone_inserts.append((int(code), map_id_counter))
                    except Exception as e:
                        print(f"⚠️ sub_zone_codes 파싱 실패: {raw} → {e}")

                map_id_counter += 1

# subzone 테이블에 삽입 (중복 제거)
subzone_inserts = list(set(subzone_inserts))
cursor.executemany(
    "INSERT OR IGNORE INTO subzone (sub_zone_code, map_id) VALUES (?, ?)",
    subzone_inserts
)

conn.commit()
conn.close()
print("✅ 모든 CSV를 map & subzone 테이블에 삽입 완료")
