import sqlite3
import csv
import ast
import json
import os

# 경로 설정
base_dir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(base_dir, "../instance")
db_path = os.path.join(base_dir, "../sqlite_data/ggg.db")
output_path = os.path.join(base_dir, "../sqlite_data/subzones.json")

# DB에서 map 테이블 전체 로딩
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT map_id, map_code, zone_code, x, y FROM map ORDER BY map_id")
map_rows = cursor.fetchall()
conn.close()

# 모든 CSV 파일을 순서대로 읽고 sub_zone_codes 추출
csv_rows = []
for filename in sorted(os.listdir(instance_dir)):
    if filename.endswith(".csv"):
        path = os.path.join(instance_dir, filename)
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_rows.append(row)

# map_id 기준으로 sub_zone_codes 병합
result = {}

for i, map_row in enumerate(map_rows):
    map_id, map_code, zone_code, x, y = map_row
    sub_zone_codes = []

    if i < len(csv_rows):
        raw_codes = csv_rows[i].get("sub_zone_codes", "").strip()
        if raw_codes:
            try:
                codes = ast.literal_eval(raw_codes)
                if isinstance(codes, list):
                    sub_zone_codes = codes
            except Exception as e:
                print(f"⚠️ map_id={map_id} sub_zone_codes 파싱 오류: {e}")

    result[map_id] = {
        "map_code": map_code,
        "zone_code": zone_code,
        "x": x,
        "y": y,
        "sub_zone_codes": sub_zone_codes
    }

# JSON 저장
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ subzones.json 생성 완료")
