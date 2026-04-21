from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

app.add_middleware(
    
    CORSMiddleware,
    allow_origins=["*"],  # en dev uniquement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Lire le CSV sans validation
        df = pd.read_csv(file.file)

        # Retour simple
        return {
            "message": "Fichier lu avec succès",
            "rows": len(df),
            "data": df.to_dict(orient="records")
        }

    except Exception as e:
        return {
            "error": "Impossible de lire le fichier CSV",
            "details": str(e)
        }