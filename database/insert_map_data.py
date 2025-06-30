import sqlite3
import csv
import os

# 경로 설정
base_dir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(base_dir, "../instance")
db_path = os.path.join(base_dir, "../sqlite_data/ggg.db")

# DB 연결
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

map_id_counter = 1

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

                cursor.execute(
                    "INSERT INTO map (map_id, map_code, zone_code, x, y) VALUES (?, ?, ?, ?, ?)",
                    (map_id_counter, map_code, zone_code, x, y)
                )
                map_id_counter += 1

conn.commit()
conn.close()
print("✅ 모든 CSV 삽입 완료")
