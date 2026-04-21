from flask import Blueprint, jsonify
from services.analytics_service import compute_ca, segment_clients
from routes.upload import DATABASE

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/ca")
def ca():
    return jsonify({"ca": compute_ca(DATABASE)})


@analytics_bp.route("/segments")
def segments():
    return jsonify(segment_clients(DATABASE))


@analytics_bp.route("/risk")
def risky():
    return jsonify([c for c in DATABASE if float(c.get("risk", 0)) > 0.7])
