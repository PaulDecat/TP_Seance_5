from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

df_global = None


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global df_global
    df_global = pd.read_csv(file.file)

    return {
        "message": "Fichier chargé",
        "rows": len(df_global)
    }


# 👇 CLASSIFICATION CLIENTS
@app.get("/clients/classification")
def classify_clients():
    global df_global

    if df_global is None:
        return {"error": "Aucune donnée"}

    def classify(row):
        ca = row["chiffre_affaires"]

        if ca < 1000:
            return "À relancer"
        elif ca < 5000:
            return "À surveiller"
        else:
            return "À fidéliser"

    df_global["category"] = df_global.apply(classify, axis=1)

    return {
        "clients": df_global.to_dict(orient="records")
    }