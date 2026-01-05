import sys
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
from .model_loader import load_model, predict as predict_image_model

app = FastAPI(title="SmartTrash AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictResponse(BaseModel):
    material: str
    bin: str
    tip: str
    color: str
    confidence: float

@app.on_event("startup")
def startup_event():
    load_model()

@app.post("/predict") # Tolto response_model per debuggare meglio
async def predict_endpoint(file: UploadFile = File(...)):
    
    print(f"\n➡️ RICHIESTA RICEVUTA! File: {file.filename}", file=sys.stderr, flush=True)

    try:
        img_bytes = await file.read()
        
        # Chiamata al model_loader
        result = predict_image_model(img_bytes)
        
        # 🚨 PROTEZIONE ANTI-CRASH 🚨
        if result is None:
            print("❌ ERRORE GRAVE: La funzione predict ha restituito None (Niente)!", file=sys.stderr)
            raise HTTPException(status_code=500, detail="Errore interno: Il modello non ha restituito dati (Controlla indentazione return)")

        if "error" in result:
             print(f"❌ ERRORE NEL MODELLO: {result['error']}", file=sys.stderr, flush=True)
             raise HTTPException(status_code=500, detail=result["error"])
             
        return result

    except Exception as e:
        print(f"❌ ERRORE GENERICO MAIN: {str(e)}", file=sys.stderr, flush=True)
        raise HTTPException(status_code=500, detail=str(e))