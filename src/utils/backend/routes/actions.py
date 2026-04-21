from flask import Blueprint, request, jsonify

actions_bp = Blueprint("actions", __name__)

ACTIONS = []

@actions_bp.route("/actions", methods=["POST"])
def create_action():
    action = request.json
    ACTIONS.append(action)
    return jsonify({"status": "created"})

@actions_bp.route("/actions")
def list_actions():
    return jsonify(ACTIONS)


@actions_bp.route("/actions/status", methods=["PUT"])
def update_status():
    body = request.json

    for a in ACTIONS:
        if a.get("id") == body["id"]:
            a["status"] = body["status"]

    return jsonify({"ok": True})
