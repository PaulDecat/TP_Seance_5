from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

# Mock de données (simule un fichier importé)
df = pd.DataFrame({
    "id": range(1, 1001),
    "name": [f"Item {i}" for i in range(1, 1001)],
    "email": [f"user{i}@test.com" for i in range(1, 1001)]
})

@app.route("/preview", methods=["GET"])
def preview():
    limit = int(request.args.get("limit", 50))

    # Limiter les données
    preview_df = df.head(limit)

    return jsonify({
        "total": len(df),
        "count": len(preview_df),
        "columns": list(preview_df.columns),
        "data": preview_df.to_dict(orient="records")
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)