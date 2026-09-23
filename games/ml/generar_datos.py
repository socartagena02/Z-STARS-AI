import random
from pathlib import Path
import pandas as pd
from features import construir_features

BASE_DIR = Path(__file__).resolve().parent


def clasificar_rendimiento(features):
    score = 0
    puntuacion = features["puntuacion_normalizada"]
    fallos = features["fallos_normalizados"]
    reaccion = features["reaccion_normalizada"]
    dificultad = features["dificultad"]

    if puntuacion >= 0.75:
        score += 3
    elif puntuacion >= 0.45:
        score += 2

    if fallos is not None:
        if fallos <= 0.25:
            score += 2
        elif fallos <= 0.60:
            score += 1

    if reaccion is not None:
        if reaccion <= 0.30:
            score += 2
        elif reaccion <= 0.60:
            score += 1

    if (dificultad == 3 and puntuacion >= 0.60):
        score += 1

    max_score = 6

    if reaccion is not None:
        max_score += 2

    ratio = score / max_score

    if ratio >= 0.70:
        return "Alto"

    if ratio >= 0.40:
        return "Intermedio"

    return "Bajo"


def generar_memorice():
    dificultad = random.randint(1, 3)
    nivel_maximo = dificultad
    puntaje = random.randrange(0, 2701, 150)
    fallos = random.randint(0, 25)
    reaccion = round(random.uniform(0.5, 3.5), 2)
    tiempo = random.randint(30, 300)

    return construir_features(
        juego="Memorice",
        puntaje=puntaje,
        tiempo_total=tiempo,
        fallos=fallos,
        dificultad=dificultad,
        nivel_maximo=nivel_maximo,
        reaccion=reaccion,
    )


def generar_simon():
    dificultad = random.randint(1, 3)
    nivel_maximo = random.randint(1, 15)
    rondas_completadas = max(nivel_maximo - 1, 0)
    puntaje = rondas_completadas * 150
    fallos = random.choice([0, 1])

    reaccion = round(random.uniform(0.5, 4.0), 2)

    tiempo = random.randint(15, 300)

    return construir_features(
        juego="Simon Dice",
        puntaje=puntaje,
        tiempo_total=tiempo,
        fallos=fallos,
        dificultad=dificultad,
        nivel_maximo=nivel_maximo,
        reaccion=reaccion,
    )


def generar_maze():
    nivel_maximo = random.randint(1, 3)

    dificultad = nivel_maximo
    fallos = random.choice([0, 1])

    puntaje = (nivel_maximo * 1000 - fallos * 100)

    puntaje = max(puntaje, 0)

    tiempo = random.randint(10,180)

    return construir_features(
        juego="Traza mi camino",
        puntaje=puntaje,
        tiempo_total=tiempo,
        fallos=fallos,
        dificultad=dificultad,
        nivel_maximo=nivel_maximo,
        reaccion=None,
    )


GENERADORES = [
    generar_memorice,
    generar_simon,
    generar_maze,
]


def generar_datos(n=6000):
    filas = []

    for _ in range(n):
        generador = random.choice(GENERADORES)
        features = generador()
        features["indicador_rendimiento"] = clasificar_rendimiento(features)
        filas.append(features)

    return pd.DataFrame(filas)


if __name__ == "__main__":
    random.seed(42)

    df = generar_datos(6000)

    ruta = (BASE_DIR / "datos_sinteticos.csv")

    df.to_csv(ruta, index=False)

    print(f"Dataset guardado en: {ruta}")

    print()
    print(df.head())
    print()
    print("Distribución general:")
    print(df["indicador_rendimiento"].value_counts())
    print()
    print("Distribución por juego:")
    print(pd.crosstab(df["juego"], df["indicador_rendimiento"],))