import os
from flask import Flask
from ggg.models import db
from ggg.routers.healthz import health_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True

# DB 초기화 및 블루프린트 등록
db.init_app(app)
app.register_blueprint(health_bp)

with app.app_context():
    db.create_all()

# 실행 진입점
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)