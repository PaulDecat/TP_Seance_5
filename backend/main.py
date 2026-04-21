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


df_global = None


# 📥 Upload CSV
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global df_global

    df_global = pd.read_csv(file.file)

    return {
        "message": "Fichier chargé",
        "rows": len(df_global)
    }



# 👇 KPI 1 : CA total (déjà fait ou optionnel)
@app.get("/kpi/revenue")
def revenue():
    global df_global

    if df_global is None:
        return {"error": "Aucune donnée"}

    return {
        "total_revenue": float(df_global["chiffre_affaires"].sum())
    }


# 👇 KPI 2 : nombre total de clients
@app.get("/kpi/clients")
def total_clients():
    global df_global

    if df_global is None:
        return {"error": "Aucune donnée"}

    return {
        "total_clients": int(df_global["client_id"].nunique())
    }