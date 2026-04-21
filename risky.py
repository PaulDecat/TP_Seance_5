def risky_clients(data):
    return [c for c in data if float(c.get("risk", 0)) > 0.7]