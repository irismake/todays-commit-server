import os
import ast
import pandas as pd
from ggg import db, create_app
from ggg.models import Zone

def load_csv():
    # korea.csv 파일 경로 설정
    base_dir = os.path.abspath(os.path.dirname(__file__))
    csv_path = os.path.join(base_dir, "..", "../instance/korea.csv")

    # CSV 읽기
    df = pd.read_csv(csv_path)
    print(f"Loaded CSV with {len(df)} rows")

    for i, row in df.iterrows():
        try:
            sub_zone_codes = ast.literal_eval(row["pnus"])  # 문자열 "[123, 456]" → 리스트 [123, 456]
            zone = Zone(
                x=int(row["x"]),
                y=int(row["y"]),
                zone_code=int(row["zone_code"]),
                sub_zone_codes=[int(p) for p in sub_zone_codes]
            )
            db.session.add(zone)
            print(f"Added row {i}: ({zone.x}, {zone.y})")
        except Exception as e:
            print(f"Error on row {i}: {e}")

    try:
        db.session.commit()
        print("DB commit successful")
    except Exception as e:
        db.session.rollback()
        print("DB commit failed:", e)

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        load_csv()
