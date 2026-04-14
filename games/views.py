from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Paciente, Partida, Institucion, Perfiles
from .serializers import PartidaSerializers
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
import json
import sys
import os
from games.ml.predict import predecir_estado
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.join(BASE_DIR, 'games', 'ml'))

def index(request):
    error = None
    if request.method == "POST":
        usuario = request.POST.get('username')
        clave = request.POST.get('password')
        
        user = authenticate(request, username=usuario, password=clave)
        
        if user is not None:
            login(request, user) 
            return redirect('dashboard') 
        else:
            error = "Usuario o contraseña incorrectos"
    
    context = {'error': error}
    return render(request, 'games/inicio-sesion.html', context)

def memorice(request):
    return render(request, 'games/memorice.html')

def simon_dice(request):
    return render(request, 'games/simon_dice.html')

@login_required
def dashboard(request):
    try:
        perfil = Perfiles.objects.get(user=request.user)
        institucion = perfil.institucion

        partidas_filtradas = Partida.objects.filter(
            paciente__institucion=institucion
        ).order_by('-fecha')

        partidas_con_prediccion = []

        for p in partidas_filtradas:
            try:
                mapa_dificultad = {
                    "Basico": 1,
                    "Intermedio": 2,
                    "Avanzado": 3
                }

                dificultad_num = mapa_dificultad.get(
                    p.nivel_dificultad,
                    1
                )

                minutos, segundos = str(p.tiempo).split(":")
                tiempo_total = int(minutos) * 60 + int(segundos)

                reaccion = float(
                    str(p.tiempo_reaccion_promedio)
                    .replace("s", "")
                    .replace(",", ".")
                )

                estado = predecir_estado(
                    fallos=int(p.fallos),
                    reaccion=reaccion,
                    puntuacion=int(p.puntaje),
                    tiempo_total=tiempo_total,
                    dificultad=dificultad_num,
                    juego=p.juego
                )

            except Exception as e:
                print("ERROR ML:", e)
                estado = "Sin datos"

            # ESTO FALTABA
            partidas_con_prediccion.append({
                'partida': p,
                'estado_cognitivo': estado
            })

        datos_graficos = list(partidas_filtradas.values(
            'paciente__nickname',
            'juego',
            'puntaje',
            'fallos',
            'tiempo_reaccion_promedio',
            'fecha',
            'nivel_dificultad'
        ))

        for d in datos_graficos:
            d['fecha'] = d['fecha'].strftime('%d/%m/%Y')

        return render(request, "games/dashboard.html", {
            'partidas': partidas_con_prediccion,
            'institucion': institucion,
            'datos_json': json.dumps(datos_graficos)
        })

    except Perfiles.DoesNotExist:
        return render(request, "games/dashboard.html", {
            'error': "No tienes un perfil asociado a una institución."
        })
        
def menuJuegos(request):
    return render(request, "games/base.html")

def contrasena(request):
    return render(request, "games/restablecer-contrasena.html")

@api_view(['get'])
def test_api(request):
    datos_prueba = {
        "Nombre_web": "Z-STARS AI",
        "servidor": "activo",
        "mensaje": "Conexión exitosa"
    }
    
    return Response(datos_prueba)

@api_view(['get'])
def lista_partida(request):
    nickname_recibido = request.data.get('apodo')
    paciente = Paciente.objects.get(nickname=nickname_recibido)
    partidas = Partida.objects.all()
    serializer = PartidaSerializers(partidas, many = True)
    return Response(serializer.data) 

@api_view(['POST'])
def puntos(request):
    nickname_recibido = request.data.get('apodo', '').strip()

    if not nickname_recibido:
        return Response(
            {"error": "No hay apodo"},
            status=status.HTTP_400_BAD_REQUEST
        )

    inst, _ = Institucion.objects.get_or_create(
        nombre="Hospital General"
    )

    try:
        paciente_instancia = Paciente.objects.get(
            nickname__iexact=nickname_recibido
        )
    except Paciente.DoesNotExist:
        paciente_instancia = Paciente.objects.create(
            nickname=nickname_recibido,
            institucion=inst
        )

    juego = request.data.get('juego')
    puntaje = int(request.data.get('puntaje', 0))
    tiempo_texto = request.data.get('tiempo', '00:00')
    fallos = int(request.data.get('fallos', 0))
    reaccion = float(request.data.get('tiempo_reaccion_promedio', 0))

    dificultad_texto = request.data.get('nivel_dificultad', 'Basico')

    maximos_puntaje = {
        "Basico": 2700,
        "Intermedio": 5400,
        "Avanzado": 8100
    }

    max_puntaje = maximos_puntaje.get(
        dificultad_texto,
        2700
    )

    puntaje_normalizado = round(
        puntaje / max_puntaje,
        2
    )

    print("Puntaje normalizado:", puntaje_normalizado)
        
    minutos, segundos = tiempo_texto.split(':')
    tiempo_total = int(minutos) * 60 + int(segundos)

    mapa_dificultad = {
        "Basico": 1,
        "Intermedio": 2,
        "Avanzado": 3
    }

    dificultad_num = mapa_dificultad.get(
        dificultad_texto,
        1
    )

    try:
        estado = predecir_estado(
            fallos=fallos,
            reaccion=reaccion,
            puntuacion=puntaje_normalizado,
            tiempo_total=tiempo_total,
            dificultad=dificultad_num,
            juego=juego
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        estado = "Sin datos"
        
    datos = request.data.copy()
    datos['estado_cognitivo'] = estado

    serializer = PartidaSerializers(data=datos)

    if serializer.is_valid():
        serializer.save(
            paciente=paciente_instancia
        )

        return Response({
            "mensaje": "Éxito",
            "estado_cognitivo": estado
        }, status=status.HTTP_201_CREATED)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

def logout(request):
    django_logout(request)
    return redirect('iniciosesion')
