import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

modelo = joblib.load(BASE_DIR / "modelo_cognitivo.pkl")

def predecir_estado(fallos, reaccion, puntuacion, tiempo_total, dificultad, juego):
    
    entrada = pd.DataFrame([{
        'fallos': fallos,
        'tiempo_reaccion_promedio': reaccion,
        'puntuacion': puntuacion,
        'tiempo_total': tiempo_total,
        'dificultad': dificultad,
        'juego': juego
    }])

    
    return modelo.predict(entrada)[0]