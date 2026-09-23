import math

DIFICULTADES = {
    "basico": 1,
    "intermedio": 2,
    "avanzado": 3,
}

def normalizar_dificultad(valor):
    if isinstance(valor, str):
        valor = valor.strip().casefold()
        if valor not in DIFICULTADES:
            raise ValueError(
                f"Dificultades desconocidas: {valor}" 
            )
            
        return DIFICULTADES[valor]
    valor = int(valor)
    
    if valor not in (1,2,3):
        raise ValueError(
            f"Dificultades fuera de rango: {valor}"
        )
    
    return valor

def puntuacion_maxima(juego, nivel_maximo):
    if juego == "Memorice":
        # 3 + 6 + 9 parejas, 150 cada una.
        return 2700.0
    
    if juego == "Simon Dice":
        '''
        Simon no tiene un máximo teórico fijo porque
        puede continuar aumentando de nivel.
        Por eso se utiliza el nivel máximo alcanzado
        como referencia de la propia sesión.
        '''
        nivel = max (int(nivel_maximo or 1), 1)
        return nivel * 150.0
    
    if juego == "Traza mi camino":
        # Tres niveles * 1000 puntos
        return 3000.0
    
    raise ValueError(
        f"Juego desconocido: {juego}"
    )

def normalizar_puntuacion(juego, puntuaje, nivel_maximo=None,):
    maximo = puntuacion_maxima(juego, nivel_maximo)
    
    if maximo <= 0:
        return 0.0
    
    valor = float(puntuaje)/maximo
    
    return round(max(0.0, min(valor, 1.0)),
        4,
    )

def normalizar_fallos(juego, fallos,):
    if fallos is None: 
        return None
    fallos = max(int(fallos), 0)
    
    if juego == "Memorice":
        ref = 20
    
    elif juego == "Simon Dice":
        ref = 1
    
    elif juego == "Traza mi camino":
        ref = 1
    
    else:
        raise ValueError(f"Juego desconocido: {juego}")
    
    return round(min(fallos/ref, 1.0), 4,)

def normalizar_reaccion(reaccion):
    if reaccion is None:
        return None
    
    reaccion = float(reaccion)
    if math.isnan(reaccion):
        return None
    
    if reaccion <= 0:
        return None
    
    valor = (reaccion - 0.5) / 3.0
    return round(max(0.0, min(valor, 1.0)), 4,)

def construir_features(juego, puntaje, tiempo_total, fallos, dificultad, nivel_maximo=None, reaccion=None,):
    dificultad_num = normalizar_dificultad(dificultad)
    return{"juego":juego, 
           "puntuacion_normalizada":
                normalizar_puntuacion(
                   juego,
                   puntaje,
                   nivel_maximo,
                   ), 
                
            "fallos_normalizados":
                normalizar_fallos(
                    juego,
                    fallos,
                ),
                
            "tiempo_total":float(tiempo_total),
            "dificultad":dificultad_num,
            "nivel_maximo_alcanzado": int(nivel_maximo or 1),
            "reaccion_normalizada":
                normalizar_reaccion(
                    reaccion
                ),
        }