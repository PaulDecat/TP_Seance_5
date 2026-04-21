from flask import Blueprint, request, jsonify
from services.csv_service import parse_csv

upload_bp = Blueprint("upload", __name__)

DATABASE = []

@upload_bp.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files["file"]
        data = parse_csv(file)
        DATABASE.extend(data)
        return jsonify({"message": "OK", "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400