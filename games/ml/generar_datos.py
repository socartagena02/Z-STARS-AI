import random
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def generar_datos(n=5000):
    datos = []

    estados = [
        'Atencion optima',
        'Estable',
        'Fatiga cognitiva'
    ]

    for _ in range(n):
        estado = random.choice(estados)

        if estado == 'Atencion optima':
            fallos = random.randint(0, 5)
            reaccion = round(random.uniform(0.5, 1.3), 2)
        elif estado == 'Estable':
            fallos = random.randint(6, 13)
            reaccion = round(random.uniform(1.4, 2.2), 2)
        else:
            fallos = random.randint(14, 28)
            reaccion = round(random.uniform(2.3, 3.5), 2)
            dificultad = random.randint(1, 3)

        puntuacion = random.randint(300, 1500)
        tiempo_total = round(random.uniform(40, 180), 2)
        juego = random.choice([
            'Simon Dice', 'Memorice'
        ])

        datos.append({
            'fallos': fallos,
            'tiempo_reaccion_promedio': reaccion,
            'puntuacion': puntuacion,
            'tiempo_total': tiempo_total,
            'dificultad': dificultad,
            'juego': juego,
            'estado_cognitivo': estado
        })

    return pd.DataFrame(datos)


df = generar_datos(2000)

ruta_csv = BASE_DIR / "datos_sinteticos.csv"
df.to_csv(ruta_csv, index=False)

print(f"CSV generado en: {ruta_csv}")
print(df.head())