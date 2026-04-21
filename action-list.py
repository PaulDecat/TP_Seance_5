@app.route("/actions/status", methods=["PUT"])
def update_status():
    body = request.json
    for a in ACTIONS:
        if a["id"] == body["id"]:
            a["status"] = body["status"]
    return {"ok": True}