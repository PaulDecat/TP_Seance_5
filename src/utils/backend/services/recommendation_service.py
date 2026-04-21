def recommend(client):
    if float(client.get("risk", 0)) > 0.7:
        return {
            "action": "relance",
            "reason": "client à risque"
        }

    return {
        "action": "upsell",
        "reason": "client stable"
    }
def explain(client):
    if float(client.get("risk", 0)) > 0.7:
        return "Risque élevé → action préventive"
    return "Client stable"