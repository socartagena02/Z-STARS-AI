from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Paciente, Partida, Institucion, Perfiles, Consentimiento
from .serializers import PartidaSerializers
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as django_logout
import json
import sys
import os
import logging
from games.ml.predict import predecir_rendimiento
from pathlib import Path
from groq import Groq
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
import resend
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db import transaction
from games.utils import pseudonimizar_nickname

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.join(BASE_DIR, 'games', 'ml'))
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'games/home.html')

def iniciosesion(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    error = None 
    if request.method == "POST":
        usuario = request.POST.get('username')
        clave = request.POST.get('password')
        
        user = authenticate(request, username=usuario, password=clave)
        
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            error = "Usuario o contraseña incorrecta"
            
    context = {'error': error}
    return render(request, 'games/inicio-sesion.html', context)

def memorice(request):
    return render(request, 'games/memorice.html')

def simon_dice(request):
    return render(request, 'games/simon_dice.html')

def maze(request):
    return render(request, 'games/maze.html')

def menuJuegos(request):
    return render(request, "games/games.html")

@login_required
def logout(request):
    if request.method == "POST":
        django_logout(request)
        return redirect('iniciosesion')
    return redirect('dashboard')

@login_required
def dashboard(request):
    try:
        perfil = Perfiles.objects.get(user=request.user)
        institucion = perfil.institucion

        if request.user.is_superuser:
            institucion = None
            partidas_filtradas = Partida.objects.filter().order_by('-fecha')
        else:
            try:
                perfil = Perfiles.objects.get(user=request.user)
                institucion = perfil.institucion
                partidas_filtradas = Partida.objects.filter(
                    paciente__profesional=request.user,
                    paciente__institucion=institucion
                ).order_by('-fecha')
            except Perfiles.DoesNotExist:
                return render(request, "games/dashboard.html",
                    {
                        'error': "No tienes un perfil asociado a una institución."
                    }
                )
        partidas_con_prediccion = []
        
        for p in partidas_filtradas:
            try:
                tiempo_str = str(p.tiempo) if p.tiempo else "00:00"

                if ":" in tiempo_str:
                    partes = tiempo_str.split(":")

                    if len(partes) >= 2:
                        minutos = int(partes[-2])
                        segundos = int(
                            float(partes[-1].replace(",", "."))
                        )
                        tiempo_total = minutos * 60 + segundos
                    else:
                        tiempo_total = 0
                else:
                    tiempo_total = (
                        int(tiempo_str)
                        if tiempo_str.isdigit()
                        else 0
                    )
                    
                reaccion = None

                if p.tiempo_reaccion_promedio is not None:
                    reaccion_texto = (
                        str(p.tiempo_reaccion_promedio)
                        .replace("s", "")
                        .replace(",", ".")
                        .strip()
                    )

                    if reaccion_texto:
                        reaccion_valor = float(reaccion_texto)

                        if reaccion_valor > 0:
                            reaccion = reaccion_valor

                resultado = predecir_rendimiento(
                    juego=p.juego,
                    puntaje=p.puntaje,
                    tiempo_total=tiempo_total,
                    fallos=p.fallos,
                    dificultad=p.nivel_dificultad,
                    nivel_maximo=p.nivel_maximo_alcanzado,
                    reaccion=reaccion,
                )

                indicador = resultado["indicador"]

            except Exception as e:
                print("ERROR ML:", e)
                indicador = "Sin datos"

            partidas_con_prediccion.append({
                "partida": p,
                "indicador_rendimiento": indicador,
            })
            
        datos_graficos = list(partidas_filtradas.values(
            'paciente__codigo_publico',
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

def registro(request):
    instituciones = Institucion.objects.all().order_by('nombre')
    institucion_seleccionada = request.POST.get('institucion', 'institucion')
    
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        institucion_id = request.POST.get('institucion')
        acepta_privacidad = request.POST.get('acepta_privacidad') == 'on'

        if not acepta_privacidad:
            return render(request, "games/registro.html",
                {
                    'error': 'Debes aceptar la Política de Privacidad para crear una cuenta',
                    'institucion_seleccionada': institucion_seleccionada,
                    'Instituciones': instituciones
                }
            )
            
        if not username or len(username) < 3:
            return render(request, "games/registro.html",
                {
                   'error': 'El nombre de usuario debe tener al menos 3 caracteres.',
                    'institucion_seleccionada': institucion_seleccionada,
                    'Instituciones': instituciones
                }
            )
        
        if User.objects.filter(username=username).exists():
           return render(request, "games/registro.html",
               {
                    'error': 'El nombre de usuario ya existe.',
                    'institucion_seleccionada': institucion_seleccionada,
                    'Instituciones': instituciones
               }
            ) 
        
        if not email:
            return render(request,"games/registro.html",
                {
                    'error': 'Debe ingresar un correo electrónico valido.',
                    'institucion_seleccionada': institucion_seleccionada,
                    'Instituciones': instituciones
                }
            )
        
        if User.objects.filter(email__iexact=email).exists():
            return render(request,"games/registro.html",
                {
                    'error': 'El correo electrónico ya existe',
                    'institucion_seleccionada': institucion_seleccionada,
                    'Instituciones': instituciones
                }
            )
            
        if password1 != password2:
            return render(request,"games/registro.html",
                {
                    'error': 'Las contraseñas no coiniciden',
                    'institucion_seleccionada': institucion_seleccionada,
                    'Instituciones': instituciones
                }
            )
            
        try:
            validate_password(password1)
        except ValidationError as e:
            return render(request,"games/registro.html",
                {
                    'error': ' '.join(e.messages),
                    'institucion_seleccionada': institucion_seleccionada,
                    'Instituciones': instituciones
                }
            )
            
        try: 
            institucion = Institucion.objects.get(pk=institucion_id)
        except (Institucion.DoesNotExist, ValueError, TypeError):
            return render(request,"games/registro.html",
                {
                    'error': 'Debes seleccionar una institución válida',
                    'institucion_seleccionada': institucion_seleccionada,
                    'Instituciones': instituciones
                }
            )
        
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password = password1
            )
            
            Perfiles.objects.create(
                user=user,
                institucion=institucion
            )
            
            Consentimiento.objects.create(
                user=user,
                tipo='tratamiento_datos',
                version='1.0',
                otorgado=True
            )
        return redirect('iniciosesion')
    
    return render(request, "games/registro.html",
            {
                'institucion_seleccionada': institucion_seleccionada,
                'instituciones': instituciones
            }
        )
    
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'games/password_reset_done.html', {
                'mensaje': 'Si el usuario existe, recibiras un link para resetear tu contraseña'
            })
        # TOKEN
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
        
        # LINK
        reset_link = f"https://www.zstars-ai.com/password-reset/{uid}/{token}/"
        # ENVIO DE EMAIL
        subject = 'Reset tu contraseña en Z-STARS AI'
        message = f"""
        Hola {user.username},
        
        Haz clic en el siguiente enlace para restablecer tu contraseña:
        {reset_link}
        
        Este enlace es válido por 1 hora.
        
        Si no solicitaste este cambio, puedes ignorar este correo.
        
        Saludos,
        Z-STARS AI
        """
        resend.api_key = os.getenv("RESEND_API_KEY")
        resend.Emails.send({
                "from": "noreply@zstars-ai.com",
                "to": [email],
                "subject": subject,
                "text": message,
            })
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
            
            try:
                validate_password(password1, user=user)
            except ValidationError as e:
                return render(request, 'games/password_reset_confirm.html', {
                    'error': ' '.join(e.messages),
                    'uidb64': uidb64,
                    'token':token
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
    
    
@api_view(['GET'])
def test_api(request):
    datos_prueba = {
        "Nombre_web": "Z-STARS AI",
        "servidor": "activo",
        "mensaje": "Conexión exitosa"
    }
    
    return Response(datos_prueba)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_partida(request):
    try:
        perfil = Perfiles.objects.get(user= request.user)
        partidas = Partida.objects.filter(
            paciente__profesional=request.user,
            paciente__institucion=perfil.institucion
        )
        
        nickname_recibido = request.query_params.get("apodo", "").strip()
        if nickname_recibido:
            pseudonimo_hash = pseudonimizar_nickname(
                nickname_recibido,
                request.user.pk,
                perfil.institucion.pk    
            )
            
            partidas = partidas.filter(
                paciente__pseudonimo_hash=pseudonimo_hash
            )
        
        serializer = PartidaSerializers(partidas, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Perfiles.DoesNotExist:
        return Response(
            {"error": "El usuario no tiene una institución asignada."},
            status=status.HTTP_403_FORBIDDEN
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def puntos(request):
    nickname_recibido = request.data.get("apodo","").strip()

    if not nickname_recibido:
        return Response({"error": "No hay apodo"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        perfil = Perfiles.objects.get(user=request.user)
        institucion = perfil.institucion

    except Perfiles.DoesNotExist:
        return Response(
            {
                "error":
                "Usuario sin institución asociada"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    pseudonimo_hash = pseudonimizar_nickname(
        nickname_recibido,
        request.user.pk,
        institucion.pk
    )

    paciente_instancia, created = (
        Paciente.objects.get_or_create(
            profesional=request.user,
            institucion=institucion,
            pseudonimo_hash=pseudonimo_hash,
        )
    )

    # --------------------------------------------------
    # Datos recibidos del juego
    # --------------------------------------------------

    juego = request.data.get("juego")

    try:
        puntaje = int(
            request.data.get("puntaje", 0) or 0
        )
    except (TypeError, ValueError):
        puntaje = 0

    tiempo_texto = request.data.get(
        "tiempo",
        "00:00"
    )

    try:
        fallos = int(
            request.data.get("fallos", 0) or 0
        )
    except (TypeError, ValueError):
        fallos = 0

    dificultad_texto = request.data.get(
        "nivel_dificultad",
        "basico"
    )

    nivel_maximo_raw = request.data.get(
        "nivel_maximo_alcanzado"
    )

    try:
        nivel_maximo = (
            int(nivel_maximo_raw)
            if nivel_maximo_raw is not None
            else None
        )
    except (TypeError, ValueError):
        nivel_maximo = None

    reaccion_raw = request.data.get(
        "tiempo_reaccion_promedio"
    )

    reaccion = None

    if reaccion_raw not in (
        None,
        "",
        "N/D",
        "null",
    ):
        try:
            reaccion_valor = float(
                reaccion_raw
            )

            if reaccion_valor > 0:
                reaccion = reaccion_valor

        except (TypeError, ValueError):
            reaccion = None

    try:
        minutos, segundos = tiempo_texto.split(
            ":"
        )[:2]

        tiempo_total = (
            int(minutos) * 60
            + int(segundos)
        )

    except (
        ValueError,
        AttributeError,
        TypeError,
    ):
        tiempo_total = 0

    try:
        resultado = predecir_rendimiento(
            juego=juego,
            puntaje=puntaje,
            tiempo_total=tiempo_total,
            fallos=fallos,
            dificultad=dificultad_texto,
            nivel_maximo=nivel_maximo,
            reaccion=reaccion,
        )

        indicador = resultado[
            "indicador"
        ]

    except Exception:
        import traceback
        traceback.print_exc()
        indicador = "Sin datos"

    datos = request.data.copy()

    datos[
        "tiempo_reaccion_promedio"
    ] = reaccion

    serializer = PartidaSerializers(
        data=datos
    )

    if serializer.is_valid():
        serializer.save(paciente=paciente_instancia)

        return Response(
            {"mensaje": "Éxito", "indicador_rendimiento": indicador, "paciente": paciente_instancia.codigo_publico},
            status=status.HTTP_201_CREATED
        )

    logger.error(
        f"Errores del serializador: "
        f"{serializer.errors}"
    )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analisis(request):
    try:
        perfil = Perfiles.objects.get(user=request.user)
        institucion = perfil.institucion

        partidas = Partida.objects.filter(
            paciente__institucion=institucion,
            paciente__profesional=request.user
        ).order_by('paciente__codigo_publico', 'fecha')

        from collections import defaultdict
        datos_pacientes = defaultdict(list)
        
        for p in partidas:
            datos_pacientes[p.paciente.codigo_publico].append({
                'juego': p.juego,
                'fallos': p.fallos,
                'reaccion': 
                    float(p.tiempo_reaccion_promedio
                    if p.tiempo_reaccion_promedio is not None
                    else None
                ),
                'dificultad': p.nivel_dificultad,
                'fecha': p.fecha.strftime('%d/%m/%Y'),
            })

        resumen = ""

        for indice, (codigo, sesiones) in enumerate(datos_pacientes.items(), start=1):
            resumen += (
                f"\nPaciente {indice}"
                f"({len(sesiones)} sesiones)\n"
            )
            
            for s in sesiones[:5]:
                reaccion = (
                    f"{s['reaccion']:.2f}s"
                    if s['reaccion'] is not None
                    else "N/D"
                )
                resumen += (
                    f"- {s['fecha']} |"
                    f"{s['juego']} |"
                    f"Fallos: {s['fallos']} |"
                    f"Reacción: {reaccion} |"
                    f"Dificultad: {s['dificultad']}\n"
                )
        
        cliente = Groq(
            api_key=os.getenv('AI_KEY')
        )

        message = cliente.chat.completions.create(
            model="openai/gpt-oss-20b",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""
                    Eres un asistente de apoyo para profesionales de rehabilitación cognitiva.
                    
                    Analiza los siguientes datos de rendimiento obtenidos en juegos cognitivos.
                    
                    Para cada paciente indica únicamente:
                    - Tendencia observada
                    - Puntos de atención
                    - Recomendación
                    
                    Usa lenguaje profesional, breve y accesible.
                    No realices diagnósticos clínicos ni atribuyas condiciones médicas.
                    Basa tus observaciones únicamente en los datos proporcionados.
                    Si una métrica aparece N/D o no está disponible, no la interpretes ni las remplaces por cero.
                    No uses tablas Markdown.
                    Evita repetir los datos innecesariamente.
                    
                    Datos:
                    {resumen}"""
                        }]
                    )

        return Response({
        'analisis': message.choices[0].message.content
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception("Error en servicio de analisis Groq")
        return Response(
            {"error": "No fue posible generar el análisis en este momento"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
def calcular_progreso(partidas):
    from collections import defaultdict
    pacientes = defaultdict(list)
    def parsear_reaccion(valor):
        if valor is None:
            return None

        texto = (
            str(valor)
            .replace("s", "")
            .replace(",", ".")
            .strip()
        )

        if texto.casefold() in {
            "",
            "none",
            "null",
            "n/d",
            "nan",
        }:
            return None

        try:
            reaccion = float(texto)
        except (TypeError, ValueError):
            return None

        if reaccion <= 0:
            return None

        return reaccion

    for p in partidas:
        pacientes[
            p.paciente.codigo_publico
        ].append({
            "fecha": p.fecha,
            "fallos": p.fallos,
            "reaccion": parsear_reaccion(
                p.tiempo_reaccion_promedio
            ),
            "juego": p.juego,
        })

    report = {}

    for codigo_publico, sesiones in pacientes.items():

        if len(sesiones) < 3:
            report[codigo_publico] = {
                "estado": "Sin datos suficientes",
                "mensaje": (
                    f"Necesita al menos 3 sesiones "
                    f"(tiene {len(sesiones)})"
                ),
            }
            continue

        sesiones_ordenadas = sorted(
            sesiones,
            key=lambda x: x["fecha"],
        )

        mitad = len(sesiones_ordenadas) // 2

        primera = sesiones_ordenadas[:mitad]
        segunda = sesiones_ordenadas[mitad:]

        fallos_primera = [
            s["fallos"]
            for s in primera
            if s["fallos"] is not None
        ]

        fallos_segunda = [
            s["fallos"]
            for s in segunda
            if s["fallos"] is not None
        ]

        fallos_antes = (
            sum(fallos_primera)
            / len(fallos_primera)
            if fallos_primera
            else None
        )

        fallos_despues = (
            sum(fallos_segunda)
            / len(fallos_segunda)
            if fallos_segunda
            else None
        )

        reaccion_primera = [
            s["reaccion"]
            for s in primera
            if s["reaccion"] is not None
        ]

        reaccion_segunda = [
            s["reaccion"]
            for s in segunda
            if s["reaccion"] is not None
        ]

        reaccion_antes = (
            sum(reaccion_primera)
            / len(reaccion_primera)
            if reaccion_primera
            else None
        )

        reaccion_despues = (
            sum(reaccion_segunda)
            / len(reaccion_segunda)
            if reaccion_segunda
            else None
        )

        mejora_fallos = None
        mejora_reaccion = None

        if (
            fallos_antes is not None
            and fallos_despues is not None
        ):
            mejora_fallos = (
                fallos_antes
                - fallos_despues
            )

        if (
            reaccion_antes is not None
            and reaccion_despues is not None
        ):
            mejora_reaccion = (
                reaccion_antes
                - reaccion_despues
            )

        mejorando = False
        empeorando = False

        if mejora_fallos is not None:
            if mejora_fallos > 2:
                mejorando = True
            elif mejora_fallos < -2:
                empeorando = True

        if mejora_reaccion is not None:
            if mejora_reaccion > 0.3:
                mejorando = True
            elif mejora_reaccion < -0.3:
                empeorando = True

        if mejorando and not empeorando:
            tendencia = "Mejorando"

        elif empeorando and not mejorando:
            tendencia = "Empeorando"

        else:
            tendencia = "Estable"

        report[codigo_publico] = {
            "estado": tendencia,
            "fallos_promedio_reciente": (
                round(fallos_despues, 1)
                if fallos_despues is not None
                else None
            ),
            "reaccion_promedio_reciente": (
                round(reaccion_despues, 2)
                if reaccion_despues is not None
                else None
            ),
            "sesiones_totales": len(sesiones),
            "mensaje": (
                f"{len(sesiones)} sesiones registradas"
            ),
        }
        
    return report