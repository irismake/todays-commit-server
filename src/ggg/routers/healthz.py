from flask import Blueprint, jsonify
from ggg.models import db
from sqlalchemy import text

health_bp = Blueprint("health", __name__, url_prefix="/healthz")

@health_bp.route("", methods=["GET"])
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"error": "DB 연결 실패", "message": str(e)}), 500

@health_bp.route("/test")
def test():
    return "<h1>Test ggg server!</h1>", 200