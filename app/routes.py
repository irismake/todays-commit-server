from flask import Blueprint, jsonify
from .models import Zone

zone_bp = Blueprint("zone", __name__)

@zone_bp.route("/")
def home():
    return "✅ Flask 서버가 작동 중입니다!"

@zone_bp.route("/coord/<int:x>/<int:y>")
def get_zone(x, y):
    zone = Zone.query.filter_by(x=x, y=y).first()
    if zone:
        return jsonify({
            "x": zone.x,
            "y": zone.y,
            "zone_code": zone.zone_code,
            "pnus": zone.pnus
        })
    return jsonify({"error": "Not found"}), 404
