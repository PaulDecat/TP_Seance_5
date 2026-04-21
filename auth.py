@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    if not check_login(data["username"], data["password"]):
        return {"error": "unauthorized"}, 401

    return {"message": "ok"}