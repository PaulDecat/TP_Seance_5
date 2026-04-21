def compute_ca(data):
    return sum(float(x.get("revenue", 0)) for x in data)
def segment_clients(data):
    result = {}
    for c in data:
        seg = c.get("segment", "unknown")
        result[seg] = result.get(seg, 0) + 1
    return result