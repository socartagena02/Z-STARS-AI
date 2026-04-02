import joblib
import pandas as pd 
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def predecir_estado(fallos, reaccion):
    modelo = joblib.load(BASE_DIR / 'modelo_cognitivo.pkl')
    encoder = joblib.load(BASE_DIR / 'label_encoder.pkl')
    
    datos_entrada = pd.DataFrame([[fallos, reaccion]], 
                                 columns=['fallos', 'tiempo_reaccion_promedio'])
    
    prediccion_num = modelo.predict(datos_entrada)
    resultado_texto = encoder.inverse_transform(prediccion_num)
    
    return resultado_texto[0]