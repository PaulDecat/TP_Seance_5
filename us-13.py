@app.get("/clients/recommendations")
def get_recommendations():
    global df_global

    if df_global is None:
        return {"error": "Aucune donnée"}

    def classify(row):
        ca = row["chiffre_affaires"]

        if ca < 1000:
            return {
                "category": "À relancer",
                "recommendation": "Relancer",
                "justification": "Le chiffre d'affaires est faible, le client est peu actif."
            }
        elif ca < 5000:
            return {
                "category": "À surveiller",
                "recommendation": "Surveiller",
                "justification": "Le chiffre d'affaires est moyen, évolution à suivre."
            }
        else:
            return {
                "category": "À fidéliser",
                "recommendation": "Fidéliser",
                "justification": "Le chiffre d'affaires est élevé, client important."
            }

    # appliquer logique
    results = df_global.apply(classify, axis=1)

    # transformer en colonnes
    df_global["category"] = results.apply(lambda x: x["category"])
    df_global["recommendation"] = results.apply(lambda x: x["recommendation"])
    df_global["justification"] = results.apply(lambda x: x["justification"])

    return {
        "clients": df_global.to_dict(orient="records")
    }