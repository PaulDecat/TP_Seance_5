from flask import Blueprint, jsonify
from services.analytics_service import compute_ca
from routes.upload import DATABASE

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/ca")
def ca():
    return jsonify({"ca": compute_ca(DATABASE)})