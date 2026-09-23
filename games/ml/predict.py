from pathlib import Path
import joblib
import pandas as pd
from .features import construir_features

BASE_DIR = Path(__file__).resolve().parent

MODEL = (BASE_DIR / "modelo_cognitivo.pkl")

model = joblib.load(MODEL)

def predecir_rendimiento(juego, puntaje, tiempo_total, fallos, dificultad, nivel_maximo=None, reaccion=None):
    features = construir_features(
        juego=juego,
        puntaje=puntaje,
        tiempo_total=tiempo_total,
        fallos=fallos,
        dificultad=dificultad,
        nivel_maximo=nivel_maximo,
        reaccion=reaccion
    )
    
    entrada = pd.DataFrame([features])
    prediccion = model.predict(entrada)[0]
    probabilidades = (
        model.predict_proba(entrada)[0]
    )
    
    clases = model.classes_
    probabilidades_dict = {
        clase: round(float(probabilidad), 4)
        for clase, probabilidad in zip(clases, probabilidades)
    }
    
    return {
        "indicador": prediccion,
        "probabilidades": probabilidades_dict,
    }