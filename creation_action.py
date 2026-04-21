ACTIONS = []

@app.route("/actions", methods=["POST"])
def create_action():
    action = request.json
    ACTIONS.append(action)
    return {"status": "created"}