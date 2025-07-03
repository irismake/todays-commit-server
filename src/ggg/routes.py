from flask import Blueprint, jsonify
from .models import User

zone_bp = Blueprint("zone", __name__)

@zone_bp.route("/test")
def test():
    return "<h1>Hello from Flask!</h1>", 200

@zone_bp.route("/")
def home():
    return "✅ Flask 서버가 작동 중입니다!"

@zone_bp.route("/user/<int:user_id>")
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            "user_id": user.user_id,
            "user_name": user.user_name,
            "created_at": user.created_at.isoformat()
        })
    return jsonify({"error": "Not found"}), 404
