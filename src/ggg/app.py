import os
from flask import Flask
from ggg.models import db  # ✅ 여기서는 기존 db 인스턴스를 import
from ggg.routes import zone_bp  # 같은 위치에 있으면 .routes 도 가능



# Flask 애플리케이션 생성 및 구성
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True

# DB 초기화 및 블루프린트 등록
db.init_app(app)
app.register_blueprint(zone_bp)

with app.app_context():
    db.create_all()

# 실행 진입점
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
