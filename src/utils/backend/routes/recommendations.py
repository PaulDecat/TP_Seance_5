from flask import Blueprint, jsonify
from services.recommendation_service import recommend
from routes.upload import DATABASE

rec_bp = Blueprint("rec", __name__)

@rec_bp.route("/recommendations")
def get_recs():
    return jsonify([recommend(c) for c in DATABASE])
