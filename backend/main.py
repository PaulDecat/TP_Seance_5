from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# CORS (important)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stockage temporaire (simple projet)
df_global = None


# Upload CSV (déjà utilisé)
@app.post("/upload")
async def upload_file(file):
    global df_global

    df_global = pd.read_csv(file.file)

    return {
        "message": "Fichier chargé",
        "rows": len(df_global)
    }


# 👉 KPI CA TOTAL
@app.get("/kpi/revenue")
def get_revenue():
    global df_global

    if df_global is None:
        return {"error": "Aucune donnée chargée"}

    total_ca = df_global["chiffre_affaires"].sum()

    return {
        "total_revenue": float(total_ca)
    }