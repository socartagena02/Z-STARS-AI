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
from groq import Groq
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string

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

        reportes_progreso = calcular_progreso(partidas_filtradas)
        print("REPORTES:", reportes_progreso)
        
        return render(request, "games/dashboard.html", {
            'partidas': partidas_con_prediccion,
            'institucion': institucion,
            'datos_json': json.dumps(datos_graficos),
            'reportes_progreso': reportes_progreso  
        })

    
    except Perfiles.DoesNotExist:
        return render(request, "games/dashboard.html", {
            'error': "No tienes un perfil asociado a una institución."
        })
        
def menuJuegos(request):
    return render(request, "games/base.html")

def registro(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'games/registro.html', {
                'error': 'Las contraseñas no coinciden'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'games/registro.html', {
                'error': 'El usuario ya existe'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        return redirect('iniciosesion')
    return render(request, "games/registro.html")

@api_view(['GET'])
def test_api(request):
    datos_prueba = {
        "Nombre_web": "Z-STARS AI",
        "servidor": "activo",
        "mensaje": "Conexión exitosa"
    }
    
    return Response(datos_prueba)

@api_view(['GET'])
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
        
    try:
        perfil = Perfiles.objects.get(user=request.user)
        institucion = perfil.institucion
    except Perfiles.DoesNotExist:
        return Response(
            {"error": "Usuario no tiene institución asociada"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        paciente_instancia = Paciente.objects.get(
            nickname__iexact=nickname_recibido
        )
    except Paciente.DoesNotExist:
        paciente_instancia = Paciente.objects.create(
            nickname=nickname_recibido,
            institucion=institucion  
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
    
def calcular_progreso(partidas):
    from collections import defaultdict
    p_p = defaultdict(list)
    
    for p in partidas:
        p_p[p.paciente.nickname].append({
            'fecha': p.fecha,
            'fallos': p.fallos,
            'reaccion': p.tiempo_reaccion_promedio,
            'juego': p.juego
        })

    report = {}
    for nickname, sesiones in p_p.items():
        if len(sesiones) < 3:
            report[nickname] = {
                'estado': 'Sin datos suficientes',
                'mensaje': f'Necesita al menos 3 sesiones (tiene {len(sesiones)})'
            }
            continue

        so = sorted(sesiones, key=lambda x: x['fecha'])
        m = len(so) // 2
        primera = so[:m]
        segunda = so[m:]

        fallos_antes = sum(s['fallos'] for s in primera) / len(primera)
        fallos_despues = sum(s['fallos'] for s in segunda) / len(segunda)
        reaccion_antes = sum(s['reaccion'] for s in primera) / len(primera)
        reaccion_despues = sum(s['reaccion'] for s in segunda) / len(segunda)

        mejora_fallos = fallos_antes - fallos_despues
        mejora_reaccion = reaccion_antes - reaccion_despues

        if mejora_fallos > 2 or mejora_reaccion > 0.3:
            tendencia = 'Mejorando'
        elif mejora_fallos < -2 or mejora_reaccion < -0.3:
            tendencia = 'Empeorando'
        else:
            tendencia = 'Estable'

        report[nickname] = {
            'estado': tendencia,
            'fallos_promedio_reciente': round(fallos_despues, 1),
            'reaccion_promedio_reciente': round(reaccion_despues, 2),
            'sesiones_totales': len(sesiones),
            'mensaje': f'{len(sesiones)} sesiones registradas'
        }

    return report

@api_view(['POST'])
def analisis(request):
    try:
        perfil = Perfiles.objects.get(user=request.user)
        institucion = perfil.institucion

        partidas = Partida.objects.filter(
            paciente__institucion=institucion
        ).order_by('paciente__nickname', 'fecha')

        from collections import defaultdict
        datos_pacientes = defaultdict(list)
        
        for p in partidas:
            datos_pacientes[p.paciente.nickname].append({
                'juego': p.juego,
                'fallos': p.fallos,
                'reaccion': float(p.tiempo_reaccion_promedio),
                'dificultad': p.nivel_dificultad,
                'fecha': p.fecha.strftime('%d/%m/%Y'),
            })

        resumen = ""
        for nickname, sesiones in datos_pacientes.items():
            resumen += f"\nPaciente: {nickname} ({len(sesiones)} sesiones)\n"
            for s in sesiones[-5:]:
                resumen += f"  - {s['fecha']} | {s['juego']} | Fallos: {s['fallos']} | Reacción: {s['reaccion']}s | Dificultad: {s['dificultad']}\n"

        cliente = Groq(
            api_key=os.getenv('AI_KEY')
        )

        message = cliente.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""Eres un asistente de apoyo para un centro de rehabilitación cognitiva o colegio.
        Analiza los siguientes datos de rendimiento de pacientes en juegos cognitivos y genera un resumen breve.
        Para cada paciente indica: tendencia general, puntos de atención y recomendación.
        Sé conciso y usa lenguaje clínico accesible. No hagas diagnósticos, solo observaciones de rendimiento.

        Datos:
        {resumen}"""
            }]
        )

        return Response({
        'analisis': message.choices[0].message.content
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'games/password_reset_done.html'), {
                'mensaje': 'Si el usuario existe, recibiras un link para resetear tu contraseña'
            }
        # TOKEN
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
        
        # LINK
        reset_link = f"https://z-stars-ai.onrender.com/password-reset/{uid}/{token}/"
        
        # ENVIO DE EMAIL
        subject = 'Reset tu contraseña en Z-STARS AI'
        message = f"""
        Buenas {user.username},
        
        Haz click en el siguiente enlace para resetear tu contraseña:
        {reset_link}
        
        Este enlace es válido por 1 hora.
        
        Si no solicitaste un reseteo, ignora este correo.
        
        Saludos,
        Z-STARS AI
        """
        send_mail(
            subject,
            message,
            'sofiacarcastro@gmail.com',
            [email],
            fail_silently=False,
        )
        return render(request, 'games/password_reset_done.html',{
         'mensaje': 'Se envio link a tu email para resetear la contraseña'   
        })
    return render(request, 'games/password_reset_request.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # Validar el Token
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 != password2:
                return render(request, 'games/password_reset_confirm.html', {
                    'error' : 'Las contraseñas no coinciden',
                    'uidb64' : uidb64,
                    'token' : token
                })
            if len(password1) < 8:
                return render(request, 'games/password_reset_confirm.html', {
                    'error' : 'la contraseña debe tener al menos 8 caracteres.',
                    'uidb4' : uidb64,
                    'token' : token
                })
            user.set_password(password1)
            user.save()
            
            return render(request, 'games/password_reset_done.html', {
                'mensaje' : 'Tu contraseña ha sido reseteada correctamente. Puedes iniciar sesión con tu nueva contraseña.',
                'success' : True
            })
        return render(request, 'games/password_reset_confirm.html', {
            'uidb64': uidb64,
            'token' : token
        })
    else:
        return render(request, 'games/password_reset_confirm.html', {
            'error': 'El link es invalido o expirado',
            'expired': True
        })
def logout(request):
    django_logout(request)
    return redirect('iniciosesion')
