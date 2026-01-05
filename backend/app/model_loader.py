import io
import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps
import os
import logging
# IMPORTANTE: Usiamo la funzione ufficiale di MobileNetV2 per la normalizzazione
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# ==========================================
# 1. CONFIGURAZIONE LOGGING
# ==========================================
logging.basicConfig(
    filename='debug_log.txt', 
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S',
    force=True
)

# ==========================================
# 2. CONFIGURAZIONE MODELLO
# ==========================================
IMG_SIZE = (224, 224)
MODEL_PATH = "app/models/best_model.h5"

# ORDINE DELLE CLASSI (Alfabetico)
CLASS_NAMES = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

# Mappatura semplice
LABEL_MAP = {
    'cardboard': 'CARTA',
    'paper':     'CARTA',
    'glass':     'VETRO',
    'plastic':   'PLASTICA',
    'metal':     'PLASTICA',
    'trash':     'INDIFFERENZIATO'
}

# Mappatura dettagliata per il Frontend
INFO_MAP = {
    'cardboard': {
        "bin": "CARTA", 
        "it": "Cartone", 
        "color": "#3498db", 
        "tip": "Appiattisci le scatole per risparmiare spazio."
    },
    'paper': {
        "bin": "CARTA", 
        "it": "Carta", 
        "color": "#3498db", 
        "tip": "Assicurati che sia pulita e senza cibo."
    },
    'glass': {
        "bin": "VETRO", 
        "it": "Vetro", 
        "color": "#2ecc71", 
        "tip": "Rimuovi il tappo (va nella plastica o metallo)."
    },
    'plastic': {
        "bin": "PLASTICA", 
        "it": "Plastica", 
        "color": "#f1c40f", 
        "tip": "Schiaccia la bottiglia per il lato lungo."
    },
    'metal': {
        "bin": "PLASTICA/METALLO", 
        "it": "Metallo", 
        "color": "#f1c40f", 
        "tip": "Sciacqua le lattine prima di buttarle."
    },
    'trash': {
        "bin": "INDIFFERENZIATO", 
        "it": "Non Riciclabile", 
        "color": "#7f8c8d", 
        "tip": "Se hai dubbi, meglio nell'indifferenziato che sbagliare."
    }
}

_model = None

def load_model():
    global _model
    logging.info(f"🔄 Tentativo caricamento modello da: {MODEL_PATH}")
    
    if os.path.exists(MODEL_PATH):
        try:
            # compile=False velocizza il caricamento
            _model = tf.keras.models.load_model(MODEL_PATH, compile=False)
            logging.info("✅ MODELLO MOBILENET V2 CARICATO CON SUCCESSO!")
        except Exception as e:
            logging.error(f"❌ CRASH caricamento modello: {str(e)}")
    else:
        logging.error(f"❌ ERRORE: File {MODEL_PATH} non trovato.")

def predict(image_bytes: bytes) -> dict:
    global _model
    
    logging.info("\n--- 📸 NUOVA RICHIESTA ANALISI ---")
    
    if _model is None: 
        return {"error": "Modello non caricato. Controlla i log."}

    try:
        # 1. Apertura Immagine
        img = Image.open(io.BytesIO(image_bytes))
        
        # 2. Correzione Orientamento (Exif)
        img = ImageOps.exif_transpose(img)
        
        # 3. Conversione RGB
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # 4. Resize
        img = img.resize(IMG_SIZE)
        
        # 5. Pre-processing MobileNetV2
        img_array = np.array(img)
        img_processed = preprocess_input(img_array)
        img_batch = np.expand_dims(img_processed, axis=0)

        # 6. Predizione
        predictions = _model.predict(img_batch)
        probs = predictions[0]

        # 7. Log Risultati
        logging.info("📊 Risultati Analisi:")
        for i, class_name in enumerate(CLASS_NAMES):
            perc = probs[i] * 100
            marker = " << VINCENTE" if perc == max(probs*100) else ""
            logging.info(f"   • {class_name.upper().ljust(10)}: {perc:.2f}% {marker}")
        
        # 8. Risultato Finale
        predicted_index = np.argmax(probs)
        confidence = float(probs[predicted_index])
        raw_label = CLASS_NAMES[predicted_index]

        info = INFO_MAP.get(raw_label)
        
        # Costruzione Risposta
        if info:
            return {
                "material": info["it"],
                "bin": info["bin"],
                "tip": info["tip"],
                "color": info["color"],
                "confidence": round(confidence, 2)
            }
        else:
            return {
                "material": raw_label,
                "bin": "INDIFFERENZIATO",
                "tip": "Nessun consiglio disponibile",
                "color": "#999999",
                "confidence": round(confidence, 2)
            }

    except Exception as e:
        logging.error(f"❌ Errore durante la predizione: {str(e)}")
        # Importante: restituiamo un dizionario con l'errore, NON None
        return {"error": str(e)}
