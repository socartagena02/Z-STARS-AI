import pandas as pd
import numpy as np
import random

def generar_datos(n_filas=1000):
    datos = []
    for _ in range(n_filas):
        estado = random.choices(
            ['Fatiga cognitiva', 'Estable', 'Atencion optima'],
            weights=[0.33, 0.34, 0.33]
        )[0]

        if estado == 'Fatiga cognitiva':
            fallos = random.randint(15, 28)
            reaccion = round(random.uniform(2.0, 3.5), 2)
        elif estado == 'Estable':
            fallos = random.randint(6, 14)
            reaccion = round(random.uniform(1.3, 2.0), 2)
        else: 
            fallos = random.randint(0, 5)
            reaccion = round(random.uniform(0.5, 1.3), 2)

        dificultad = random.choice([1, 2, 3])
        datos.append([fallos, reaccion, dificultad, estado])

    df = pd.DataFrame(datos, columns=[
        'fallos', 'tiempo_reaccion_promedio', 
        'dificultad', 'estado_cognitivo'
    ])
    df.to_csv('datos_sinteticos.csv', index=False)
    print("Dataset creado con 1000 filas.")

generar_datos()