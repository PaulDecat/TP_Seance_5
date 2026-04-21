from flask import Blueprint, request, jsonify
from services.auth_service import check_login

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    ok = check_login(data["username"], data["password"])

    if not ok:
        return jsonify({"error": "invalid"}), 401

    return jsonify({"message": "ok"})
