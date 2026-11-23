from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Paciente, Partida, Institucion, Perfiles, Consentimiento, TwoFactorAuth
from .serializers import PartidaSerializers
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as django_logout
from games.ml.predict import predecir_rendimiento
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from pathlib import Path
from groq import Groq
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from games.utils import pseudonimizar_nickname
from django_ratelimit.decorators import ratelimit
from django.urls import reverse
from django.db.models import Avg
from games.decorators import requiere_rol
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings

import hashlib
import json
import secrets
import sys
import os
import logging
import math
import io
import base64
import pyotp
import qrcode
import resend
import time

from django.contrib.auth import get_user_model

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.join(BASE_DIR, 'games', 'ml'))
logger = logging.getLogger(__name__)

User = get_user_model()

def index(request):
    return render(request, 'games/home.html')

PENDIENTE_2FA_TTL = 300

@ratelimit(key="ip", rate="5/m", method="POST", block=False)
def iniciosesion(request):
    if request.user.is_authenticated:
        return redireccion_por_rol(request.user)
    
    error = None 
    if request.method == "POST":
        
        if getattr(request, "limited", False):
            return render(
                request,
                "games/inicio-sesion.html",
                {"error":
                    "Demasiados intentos. "
                    "Espera un momento antes de intentarlo de nuevo."
                },
                status=429, 
            )
            
        usuario = request.POST.get('username', '').strip()
        clave = request.POST.get('password')
        
        user = authenticate(request, username=usuario, password=clave)
        
        if user is not None:
            tiene_2FA = TwoFactorAuth.objects.filter(
                user=user,
                is_enabled=True    
            ).exists()
            
            if tiene_2FA:
                request.session.pop("2fa_pendiente", None)
                
                request.session["2fa_pendiente"] = {
                    "user_id": user.pk,
                    "desde": timezone.now().timestamp(),
                    "backend": user.backend,
                }
                
                return redirect("login_2fa")
            
            auth_login(request, user)
            return redireccion_por_rol(user)
        else:
            error = "Usuario o contraseña incorrecta"
            
    
    return render(request, 'games/inicio-sesion.html', {'error': error})

def validar_totp_anti_replay(user, codigo):
    if not codigo or not codigo.isdigit() or len(codigo) != 6:
        return False

    with transaction.atomic():
        two_factor = (
            TwoFactorAuth.objects
            .select_for_update()
            .filter(user=user, is_enabled=True)
            .first()
        )

        if two_factor is None:
            return False

        secret = two_factor.get_secret()

        if not secret:
            return False

        totp = pyotp.TOTP(secret)

        contador_actual = int(time.time() // totp.interval)

        contadores_candidatos = [
            contador_actual - 1,
            contador_actual,
            contador_actual + 1,
        ]

        contadores_coincidentes = [
            contador
            for contador in contadores_candidatos
            if totp.generate_otp(contador) == codigo
        ]

        contadores_nuevos = [
            contador
            for contador in contadores_coincidentes
            if contador > two_factor.last_used_counter
        ]

        if not contadores_nuevos:
            return False

        contador_validado = max(contadores_nuevos)

        two_factor.last_used_counter = contador_validado

        two_factor.save(
            update_fields=["last_used_counter"]
        )

        return True

@ratelimit(key="ip", rate="5/m", method="POST", block=False)
def login_2fa(request):
    if request.user.is_authenticated:
        return redireccion_por_rol(request.user)

    pendiente = request.session.get("2fa_pendiente")

    if not pendiente:
        return redirect("iniciosesion")

    desde = pendiente.get("desde")

    if desde is None:
        request.session.pop("2fa_pendiente", None)
        return redirect("iniciosesion")

    tiempo_transcurrido = timezone.now().timestamp() - desde
    
    if tiempo_transcurrido > PENDIENTE_2FA_TTL:
        request.session.pop("2fa_pendiente", None)
        return redirect("iniciosesion")
    
    if tiempo_transcurrido < 0:
        request.session.pop("2fa_pendiente", None)
        return redirect("iniciosesion")

    User = get_user_model()

    try:
        user = User.objects.get(
            pk=pendiente.get("user_id"),
            is_active=True
        )
    except (User.DoesNotExist, TypeError, ValueError):
        request.session.pop("2fa_pendiente", None)
        return redirect("iniciosesion")

    error = None

    if request.method == "POST":

        if getattr(request, "limited", False):
            return render(
                request,
                "games/login-2fa.html",
                {
                    "error": (
                        "Demasiados intentos. "
                        "Espera un momento antes de intentarlo nuevamente."
                    )
                },
                status=429,
            )

        codigo = request.POST.get("codigo", "").strip()

        if validar_totp_anti_replay(user, codigo):
            
            backend = pendiente.get("backend")

            if backend not in settings.AUTHENTICATION_BACKENDS:
                request.session.pop("2fa_pendiente", None)
                return redirect("iniciosesion")

            request.session.pop("2fa_pendiente", None)

            auth_login(
                request,
                user,
                backend=backend
            )

            return redireccion_por_rol(user)

        error = "Código incorrecto, vencido o ya utilizado."

    return render(
        request,
        "games/login-2fa.html",
        {"error": error}
    )

@requiere_rol('paciente')
def memorice(request):
    return render(request, 'games/memorice.html')

@requiere_rol('paciente')
def simon_dice(request):
    return render(request, 'games/simon_dice.html')

@requiere_rol('paciente')
def maze(request):
    return render(request, 'games/maze.html')

@requiere_rol('paciente')
def menuJuegos(request):
    return render(request, "games/games.html")

@login_required
def logout(request):
    if request.method == "POST":
        django_logout(request)
        return redirect('iniciosesion')
    return redirect('dashboard')

@login_required
@require_POST
def desactivar_cuenta(request):
    user = request.user

    user.is_active = False
    user.save(update_fields=["is_active"])

    logout(request)

    return redirect("iniciosesion")

@requiere_rol('paciente', 'profesional')
def config(request):
    return render(request, "games/config/index.html", {
            "page_heading": "Configuración",        
        }
    )

def generar_qr_2fa(uri):
    qr = qrcode.make(uri)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")

    imagen_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return f"data:image/png;base64,{imagen_base64}"


@requiere_rol('paciente', 'profesional')
@ratelimit(key="user", rate="5/10m", method="POST", block=False)
def security(request):
    two_factor, _ = TwoFactorAuth.objects.get_or_create(
        user=request.user
    )

    error = None
    qr_url = None
    manual_key = None
    configuracion_pendiente = False

    if request.method == "POST":

        if getattr(request, "limited", False):
            error = (
                "Demasiados intentos. "
                "Espera unos minutos antes de continuar."
            )

        else:
            accion = request.POST.get("accion")

            if accion == "configurar":

                if two_factor.is_enabled:
                    error = "La autenticación en dos pasos ya está activa."

                else:
                    secret = pyotp.random_base32()

                    two_factor.set_pending_secret(secret)
                    two_factor.save(
                        update_fields=["pending_secret"]
                    )

                    request.session["2fa_setup_started"] = (
                        timezone.now().timestamp()
                    )

                    totp = pyotp.TOTP(secret)

                    uri = totp.provisioning_uri(
                        name=request.user.email or request.user.username,
                        issuer_name="Z-STARS AI",
                    )

                    qr_url = generar_qr_2fa(uri)
                    manual_key = secret
                    configuracion_pendiente = True

            elif accion == "verificar":

                secret = two_factor.get_pending_secret()

                inicio = request.session.get(
                    "2fa_setup_started"
                )

                expirado = (
                    not inicio
                    or timezone.now().timestamp() - inicio > 600
                )

                if not secret or expirado:
                    two_factor.clear_pending_secret()
                    two_factor.save(
                        update_fields=["pending_secret"]
                    )

                    request.session.pop(
                        "2fa_setup_started",
                        None
                    )

                    error = (
                        "La configuración expiró. "
                        "Genera un nuevo código QR."
                    )

                else:
                    codigo = request.POST.get("codigo", "").strip()

                    totp = pyotp.TOTP(secret)

                    if totp.verify(
                        codigo,
                        valid_window=1
                    ):
                        two_factor.set_secret(secret)
                        two_factor.clear_pending_secret()
                        two_factor.is_enabled = True

                        two_factor.save(
                            update_fields=[
                                "secret_key",
                                "pending_secret",
                                "is_enabled",
                            ]
                        )

                        request.session.pop(
                            "2fa_setup_started",
                            None
                        )

                        messages.success(
                            request,
                            "Autenticación en dos pasos activada correctamente."
                        )

                        return redirect("seguridad")

                    error = (
                        "El código ingresado no es válido. "
                        "Inténtalo nuevamente."
                    )

                    configuracion_pendiente = True

                    totp = pyotp.TOTP(secret)

                    uri = totp.provisioning_uri(
                        name=request.user.email or request.user.username,
                        issuer_name="Z-STARS AI",
                    )

                    qr_url = generar_qr_2fa(uri)
                    manual_key = secret

            elif accion == "cancelar":

                two_factor.clear_pending_secret()
                two_factor.save(
                    update_fields=["pending_secret"]
                )

                request.session.pop(
                    "2fa_setup_started",
                    None
                )

                messages.info(
                    request,
                    "Configuración de 2FA cancelada."
                )

                return redirect("seguridad")
            
    if (request.method == "GET" and not two_factor.is_enabled and two_factor.pending_secret):
        inicio = request.session.get(
            "2fa_setup_started"
        )

        if (inicio and timezone.now().timestamp() - inicio <= 600):
            secret = two_factor.get_pending_secret()

            totp = pyotp.TOTP(secret)

            uri = totp.provisioning_uri(
                name=request.user.email or request.user.username,
                issuer_name="Z-STARS AI",
            )

            qr_url = generar_qr_2fa(uri)
            manual_key = secret
            configuracion_pendiente = True

        else:
            two_factor.clear_pending_secret()
            two_factor.save(
                update_fields=["pending_secret"]
            )

            request.session.pop(
                "2fa_setup_started",
                None
            )

    return render(
        request,
        "games/config/security.html",
        {
            "page_heading": "Seguridad",
            "two_factor_enabled": two_factor.is_enabled,
            "qr_url": qr_url,
            "manual_key": manual_key,
            "configuracion_pendiente": configuracion_pendiente,
            "error_2fa": error,
        }
    )

def generar_request_hash(datos, pseudonimo_hash):
    contenido = {
        "paciente": pseudonimo_hash,
        "juego": datos["juego"],
        "puntaje": datos["puntaje"],
        "fallos": datos["fallos"],
        "dificultad": datos["dificultad"],
        "tiempo": datos["tiempo_texto"],
        "nivel_maximo": datos["nivel_maximo"],
        "reaccion": datos["reaccion"],
    }

    contenido_json = json.dumps(
        contenido,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return hashlib.sha256(
        contenido_json.encode("utf-8")
    ).hexdigest()
    
@requiere_rol('paciente', 'profesional')
def profile(request):
    profile_user = request.user

    profile = (
        Perfiles.objects
        .filter(user=profile_user)
        .select_related("institucion")
        .first()
    )

    rol = profile.rol if profile else None
    modalidad = profile.modalidad if profile else None
    
    paciente = None
    institucion = profile.institucion if profile else None
    
    if rol == "paciente":
        paciente = Paciente.objects.filter(user=profile_user).first()
        institucion = profile.institucion if profile else None

    if request.method == "POST":
        nickname = request.POST.get("nickname", "").strip()
        email = request.POST.get("email", "").strip().lower()
        current_password = request.POST.get("current_password", "")

        if not current_password:
            messages.error(
                request,
                "Debes ingresar tu contraseña actual para confirmar los cambios."
            )

        elif not profile_user.check_password(current_password):
            messages.error(
                request,
                "La contraseña actual es incorrecta."
            )

        elif not nickname or not email:
            messages.error(
                request,
                "El nombre de usuario y el correo son obligatorios."
            )

        elif User.objects.filter(
            username=nickname
        ).exclude(pk=profile_user.pk).exists():
            messages.error(
                request,
                "Ese nombre de usuario ya está ocupado."
            )

        elif User.objects.filter(
            email__iexact=email
        ).exclude(pk=profile_user.pk).exists():
            messages.error(
                request,
                "Ese correo electrónico ya está registrado."
            )

        else:
            profile_user.username = nickname
            profile_user.email = email

            profile_user.save(
                update_fields=["username", "email"]
            )

            messages.success(
                request,
                "Tu perfil se actualizó correctamente."
            )

            return redirect("profile")

    return render(request, "games/profile.html", {
        "page_heading": "Perfil",
        "rol": rol,
        "modalidad": modalidad,
        "institucion": institucion,
        "paciente": paciente,
    })

def redireccion_por_rol(user):
    if user.is_superuser:
        return redirect('dashboard')

    perfil = Perfiles.objects.filter(user=user).first()
    
    if not perfil:
        # django_logout(None)
        return redirect('iniciosesion') 
    
    if perfil.rol == 'profesional':
        return redirect('dashboard')
    
    if perfil.rol == 'paciente':
        return redirect('menu_juegos')
    
    return redirect('home')

@login_required
@requiere_rol('paciente')
def mis_partidas(request):
    paciente = Paciente.objects.filter(user=request.user).first()

    if paciente is None:
        return render(request, 'games/partidas.html', {
            'partidas': [],
            'error': 'Tu cuenta no está vinculada a un paciente.',
        })

    queryset = Partida.objects.filter(
        paciente=paciente
    ).order_by('-fecha')

    paginator = Paginator(queryset, 10)  
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'games/partidas.html', {
        'partidas': page_obj,
        'page_obj': page_obj,
        'page_heading': 'Mis partidas',
    })

@requiere_rol('profesional')
def dashboard(request):
    if request.user.is_superuser:
        institucion = None
        partidas_filtradas = Partida.objects.all().order_by("-fecha")
        total_pacientes = Paciente.objects.count()

    else:
        try:
            perfil = Perfiles.objects.select_related("institucion").get(user=request.user)

            institucion = perfil.institucion

            partidas_filtradas = Partida.objects.filter(paciente__profesional=request.user).order_by("-fecha")

            pacientes_profesional = Paciente.objects.filter(profesional=request.user)

            total_pacientes = pacientes_profesional.count()

        except Perfiles.DoesNotExist:
            return render(
                request,
                "games/dashboard.html",
                {"error": "No tienes un perfil asociado."}
            )
       
    partidas_con_prediccion = []
    total_sesiones = partidas_filtradas.count()

    conteo_dificultad = {
        "basico": 0,
        "intermedio": 0,
        "avanzado": 0,
    }

    for p in partidas_filtradas:
        nivel = (p.nivel_dificultad or "").strip().casefold()

        if nivel in conteo_dificultad:
            conteo_dificultad[nivel] += 1

        indicador = "Sin datos"

        try:
            tiempo_str = str(p.tiempo) if p.tiempo else "00:00"
            partes = tiempo_str.split(":")

            if len(partes) == 2:
                minutos = int(partes[0])
                segundos = int(float(partes[1].replace(",", ".")))
                tiempo_total = minutos * 60 + segundos
            else:
                tiempo_total = 0

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

                    if math.isfinite(reaccion_valor) and reaccion_valor > 0:
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

        except Exception:
            logger.exception(
                "Error al calcular indicador de rendimiento"
            )

        partidas_con_prediccion.append({
            "partida": p,
            "indicador_rendimiento": indicador,
        })

    total_dificultad = sum(conteo_dificultad.values())

    if total_dificultad:
        porcentaje_basico = (
            conteo_dificultad["basico"] / total_dificultad * 100
        )
        porcentaje_intermedio = (
            conteo_dificultad["intermedio"] / total_dificultad * 100
        )
        porcentaje_avanzado = (
            conteo_dificultad["avanzado"] / total_dificultad * 100
        )
    else:
        porcentaje_basico = 0
        porcentaje_intermedio = 0
        porcentaje_avanzado = 0

    datos_graficos = list(
        partidas_filtradas.order_by("fecha").values(
            "paciente__codigo_publico",
            "juego",
            "puntaje",
            "fallos",
            "tiempo_reaccion_promedio",
            "fecha",
            "nivel_dificultad",
        )
    )

    for numero, partida in enumerate(datos_graficos, start=1):
        partida["sesion"] = numero
        partida["fecha"] = partida["fecha"].strftime("%d/%m/%Y")

    reportes_progreso = calcular_progreso(partidas_filtradas)

    puntos_progreso = [
        {
            "x": d["sesion"],
            "y": d["puntaje"],
            "juego": d["juego"],
            "paciente": d["paciente__codigo_publico"],
        }
        for d in datos_graficos
    ]

    promedio = partidas_filtradas.aggregate(
        promedio_fallos=Avg("fallos"),
        promedio_reaccion=Avg("tiempo_reaccion_promedio"),
    )

    promedio_fallos = (
        round(promedio["promedio_fallos"], 1)
        if promedio["promedio_fallos"] is not None
        else 0
    )

    promedio_reaccion = (
        round(promedio["promedio_reaccion"], 2)
        if promedio["promedio_reaccion"] is not None
        else 0
    )
        
    return render(request, "games/dashboard.html", {
        'partidas': partidas_con_prediccion,
        'institucion': institucion,
        'datos_graficos': datos_graficos,
        'reportes_progreso': reportes_progreso,
        'conteo_dificultad': conteo_dificultad,
        'porcentaje_basico': porcentaje_basico,
        'porcentaje_intermedio': porcentaje_intermedio,
        'porcentaje_avanzado': porcentaje_avanzado,
        'total_dificultad': total_dificultad,
        'total_pacientes': total_pacientes,
        'total_sesiones': total_sesiones,
        'puntos_progreso': puntos_progreso,
        'promedio_fallos': promedio_fallos,
        'promedio_reaccion': promedio_reaccion
    })

def registro(request):
    instituciones = Institucion.objects.all().order_by('nombre')
    
    context = {
        'instituciones': instituciones,
        'institucion_seleccionada': '',
        'error': None,
    }
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        rol = request.POST.get('rol', '').strip()
        modalidad = request.POST.get('modalidad', '').strip()
        institucion_id = request.POST.get('institucion', '').strip()
        
        acepta_privacidad = request.POST.get('acepta_privacidad')
        aceptar_mayoria = request.POST.get('aceptar_mayoria')
        
        context['institucion_seleccionada'] = institucion_id
        
        error = None
        
        institucion = None
        
        if not acepta_privacidad:
            error = 'Debes aceptar el tratamiento de datos para crear una cuenta.'
            
        if aceptar_mayoria != 'on':
            error = "Debes declarar que tienes 18 años o más para registrarte."
        
        elif len(username) < 3:
            error = 'El nombre de usuario debe tener al menos 3 caracteres.'
        
        elif User.objects.filter(username=username).exists():
            error = 'El nombre de usuario ya está registrado.'
        
        elif not email:
            error = 'Debes ingresar un correo electrónico.'
        
        elif User.objects.filter(email__iexact=email).exists():
            error = 'El correo electrónico ya está registrado.'
            
        elif not password1 or not password2:
            error = 'Debes completar ambas contraseñas.'
        
        elif password1 != password2:
            error = 'Las contraseñas no coinciden.'
        
        else:
            try:
                validate_password(password1)
            except ValidationError as e:
                error = ' '.join(e.messages)
                
        if not error:
            if rol not in ['paciente', 'profesional']:
                error = 'El rol seleccionado no es valido'
        
        if not error:
            if rol == 'paciente':
                modalidad = None
                institucion = None
            
            elif rol == 'profesional':
                if modalidad not in ['institucional', 'independiente']:
                    error = 'Debes seleccionar una modalidad válida.'
                
                elif modalidad == 'institucional':

                    if not institucion_id:
                        error = 'Debes seleccionar una institución.'
                    else:
                        try:
                            institucion = Institucion.objects.get(
                                pk=institucion_id
                            )
                        except Institucion.DoesNotExist:
                            error = 'La institución seleccionada no es válida.'
                elif modalidad == 'independiente':
                    institucion = None
        
        if not error:
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password1
                    )
                    
                    Perfiles.objects.create(
                        user=user,
                        rol=rol,
                        modalidad=modalidad,
                        institucion=institucion
                    )
                    
                    if rol == 'paciente':
                        pseudonimo_hash = hashlib.sha256(
                            secrets.token_bytes(32)
                        ).hexdigest()
                        
                        Paciente.objects.create(
                            user=user,
                            pseudonimo_hash=pseudonimo_hash,
                            institucion=None,
                            profesional=None
                        )
                    
                    Consentimiento.objects.create(
                        user=user,
                        tipo='tratamiento_datos',
                        version='1.0',
                        otorgado=True
                    )
                
                return redirect('iniciosesion')
                
            except Exception:
                logger.exception("Error durante el registro de usuario")
                error = (
                    'No fue posible completar el registro '
                    'Intentalo nuevamente.'
                )
        
        context['error'] = error
    return render(request, "games/registro.html", context)

@ratelimit(key="ip", rate="3/10m", method="POST", block=False)
def password_reset_request(request):
    mensaje = ("Si el correo está registrado, recibirás instrucciones "
        "para restablecer la contraseña."
    )

    if request.method != "POST":
        return render(request, "games/password_reset_request.html")

    if getattr(request, "limited", False):
        return render(request, "games/password_reset_done.html", {"mensaje": mensaje}, status=429)

    email = request.POST.get("email", "").strip().lower()

    user = User.objects.filter(
        email__iexact=email
    ).first()

    if user is not None:
        try:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_path = reverse(
                "password_reset_confirm",
                kwargs={
                    "uidb64": uid,
                    "token": token,
                },
            )

            reset_link = request.build_absolute_uri(reset_path)

            subject = "Restablece tu contraseña en Z-STARS AI"

            message = f"""
                Hola {user.username},

                Haz clic en el siguiente enlace para restablecer tu contraseña:

                {reset_link}

                Si no solicitaste este cambio, puedes ignorar este correo.

                Saludos,
                Z-STARS AI
                """

            resend.api_key = os.getenv("RESEND_API_KEY")

            resend.Emails.send({
                "from": "noreply@zstars-ai.com",
                "to": [user.email],
                "subject": subject,
                "text": message,
            })

        except Exception:
            logger.exception(
                "Error al enviar correo de recuperación"
            )

    return render(
        request,
        "games/password_reset_done.html",
        {"mensaje": mensaje}
    )
@ratelimit(key="ip", rate="5/10m", method="POST", block=False)
def password_reset_confirm(request, uidb64, token):
    if request.method == "POST" and getattr(request, "limited", False):
        return render(request, "games/password_reset_confirm.html", {
                "error": "Demasiados intentos. Intenta nuevamente más tarde.",
                "uidb64": uidb64,
                "token": token,
            },
            status=429,
        )
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if not password1 or not password2:
                return render(request, 'games/password_reset_confirm.html', {
                    'error': 'Faltan campos',
                    'uidb64' : uidb64,
                    'token' : token
                })
            
            if password1 != password2:
                return render(request,'games/password_reset_confirm.html',
                    {   
                        'error' : 'Las contraseñas no coinciden',
                        'uidb64': uidb64,
                        'token': token,
                    }
                )
            
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
            'error': 'El enlace es inválido o ha expirado',
            'expired': True
        })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lista_partida(request):
    try:
        perfil = Perfiles.objects.select_related(
            "institucion"
        ).get(user=request.user)

    except Perfiles.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil asociado."},
            status=status.HTTP_403_FORBIDDEN
        )

    if perfil.rol == "profesional":
        return Response(
            {"error": "No tienes permisos para consultar partidas."},
            status=status.HTTP_403_FORBIDDEN
        )

    partidas = Partida.objects.filter(paciente__profesional=request.user).select_related("paciente").order_by("-fecha")

    nickname = request.query_params.get("apodo", "").strip()
    if nickname:
        pseudonimo_hash = pseudonimizar_nickname(
            nickname,
            request.user.pk,
            perfil.institucion.pk if perfil.institucion else None
        )

        partidas = partidas.filter(
            paciente__pseudonimo_hash=pseudonimo_hash
        )
        
    serializer = PartidaSerializers(partidas, many=True)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )

def convertir_entero(valor, nombre):
    if isinstance(valor, bool):
        raise ValueError(
            f"{nombre} debe ser un número entero."
        )

    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ValueError(
            f"{nombre} debe ser un número entero."
        )

    if not math.isfinite(numero) or not numero.is_integer():
        raise ValueError(
            f"{nombre} debe ser un número entero."
        )

    return int(numero)

def validar_datos_partida(data):
    juegos_validos = {"Memorice", "Simon Dice", "Traza mi camino"}
    dificultades_validas = {"basico", "intermedio", "avanzado"}

    juego = str(data.get("juego", "")).strip()

    if juego not in juegos_validos:
        raise ValueError("Juego no válido.")

    puntaje = convertir_entero(data.get("puntaje"), "el puntaje")
    fallos = convertir_entero(data.get("fallos"), "los fallos")

    if puntaje < 0:
        raise ValueError("El puntaje no puede ser negativo.")

    if fallos < 0:
        raise ValueError("La cantidad de fallos no puede ser negativa.")

    dificultad = str(
        data.get("nivel_dificultad", "")
    ).strip().casefold()

    if dificultad not in dificultades_validas:
        raise ValueError("Nivel de dificultad no válido.")

    tiempo_texto = str(data.get("tiempo", "")).strip()

    try:
        partes = tiempo_texto.split(":")

        if len(partes) != 2:
            raise ValueError

        minutos = int(partes[0])
        segundos = int(partes[1])

        if minutos < 0 or segundos < 0 or segundos > 59:
            raise ValueError

    except (TypeError, ValueError):
        raise ValueError("Formato de tiempo no válido.")

    tiempo_total = minutos * 60 + segundos

    nivel_raw = data.get("nivel_maximo_alcanzado")

    if nivel_raw in (None, ""):
        nivel_maximo = None
    else:
        nivel_maximo = convertir_entero(
            nivel_raw,
            "el nivel máximo"
        )

        if nivel_maximo < 1:
            raise ValueError(
                "El nivel máximo debe ser mayor que cero."
            )

    reaccion_raw = data.get("tiempo_reaccion_promedio")

    if reaccion_raw in (None, "", "N/D", "null"):
        reaccion = None
    else:
        try:
            reaccion = float(reaccion_raw)
        except (TypeError, ValueError):
            raise ValueError(
                "El tiempo de reacción debe ser numérico."
            )

        if not math.isfinite(reaccion) or reaccion <= 0:
            raise ValueError(
                "El tiempo de reacción debe ser mayor que cero."
            )

    return {
        "juego": juego,
        "puntaje": puntaje,
        "fallos": fallos,
        "dificultad": dificultad,
        "tiempo_texto": tiempo_texto,
        "tiempo_total": tiempo_total,
        "nivel_maximo": nivel_maximo,
        "reaccion": reaccion,
    }

def validar_reglas_juego(datos):
    juego = datos["juego"]
    puntaje = datos["puntaje"]
    fallos = datos["fallos"]
    dificultad = datos["dificultad"]
    nivel_maximo = datos["nivel_maximo"]
    reaccion = datos["reaccion"]

    if juego == "Traza mi camino":
        if fallos not in (0, 1):
            raise ValueError(
                "Cantidad de fallos no válida para Traza mi camino."
            )

        if nivel_maximo is None:
            raise ValueError(
                "Traza mi camino debe informar el nivel alcanzado."
            )

        if nivel_maximo not in (1, 2, 3):
            raise ValueError(
                "Nivel no válido para Traza mi camino."
            )

        dificultad_esperada = {
            1: "basico",
            2: "intermedio",
            3: "avanzado",
        }[nivel_maximo]

        if dificultad != dificultad_esperada:
            raise ValueError(
                "La dificultad no corresponde al nivel alcanzado."
            )

        if reaccion is not None:
            raise ValueError(
                "Traza mi camino no utiliza tiempo de reacción."
            )

        puntaje_esperado = nivel_maximo * 1000 - fallos * 100

        if puntaje != max(0, puntaje_esperado):
            raise ValueError(
                "La puntuación no corresponde a una partida válida "
                "de Traza mi camino."
            )

    elif juego == "Memorice":
        if fallos < 0:
            raise ValueError("Cantidad de fallos no válida.")

        if puntaje % 150 != 0:
            raise ValueError(
                "La puntuación no es válida para Memorice."
            )

        if puntaje > 2700:
            raise ValueError(
                "El puntaje excede el máximo de Memorice."
            )

        if nivel_maximo is not None:
            raise ValueError(
                "Memorice no utiliza nivel máximo alcanzado."
            )

    elif juego == "Simon Dice":
        if puntaje % 150 != 0:
            raise ValueError(
                "La puntuación no es válida para Simón Dice."
            )

        if nivel_maximo is None or nivel_maximo < 1:
            raise ValueError(
                "Simón Dice debe informar un nivel alcanzado válido."
            )

        if puntaje != (nivel_maximo - 1) * 150:
            raise ValueError(
                "La puntuación no corresponde al nivel alcanzado."
            )

        if fallos != 1:
            raise ValueError(
                "Cantidad de fallos no válida para Simón Dice."
            )
        
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@ratelimit(key="user", rate="30/m", method="POST", block=False)
def puntos(request):
    if getattr(request, "limited", False):
        return Response(
            {"error": "Demasiadas solicitudes. Intenta nuevamente más tarde."},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
        
    try:
        perfil = Perfiles.objects.select_related(
            "institucion"
        ).get(user=request.user)

    except Perfiles.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil asociado."},
            status=status.HTTP_403_FORBIDDEN
        )

    if perfil.rol not in ("profesional", "paciente"):
        return Response(
            {"error": "Rol no autorizado."},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        datos_validados = validar_datos_partida(request.data)
        validar_reglas_juego(datos_validados)

    except ValueError as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_400_BAD_REQUEST
        )

    paciente_instancia = None
    pseudonimo_hash = None
    institucion = perfil.institucion

    if perfil.rol == "profesional":

        nickname = request.data.get("apodo")

        if not isinstance(nickname, str):
            return Response(
                {"error": "El apodo debe ser un texto válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        nickname = nickname.strip()

        if not nickname or len(nickname) > 50:
            return Response(
                {"error": "El apodo no es válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        pseudonimo_hash = pseudonimizar_nickname(
            nickname,
            request.user.pk,
            institucion.pk if institucion else None,
        )

        identidad_partida = pseudonimo_hash

    elif perfil.rol == "paciente":

        paciente_instancia = Paciente.objects.filter(
            user=request.user
        ).first()

        if not paciente_instancia:
            return Response(
                {"error": "No existe un paciente asociado a tu cuenta."},
                status=status.HTTP_404_NOT_FOUND
            )

        identidad_partida = f"paciente:{paciente_instancia.pk}"

    datos = {
        "idempotency_key": request.data.get("idempotency_key"),
        "juego": datos_validados["juego"],
        "puntaje": datos_validados["puntaje"],
        "fallos": datos_validados["fallos"],
        "nivel_dificultad": datos_validados["dificultad"],
        "tiempo": datos_validados["tiempo_texto"],
        "tiempo_reaccion_promedio": datos_validados["reaccion"],
        "nivel_maximo_alcanzado": datos_validados["nivel_maximo"],
    }

    serializer = PartidaSerializers(data=datos)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        
    request_hash = generar_request_hash(
        datos_validados,
        identidad_partida
    )

    idempotency_key = serializer.validated_data["idempotency_key"]

    partida_existente = Partida.objects.select_related(
        "paciente"
    ).filter(
        idempotency_key=idempotency_key
    ).first()

    if partida_existente:

        pertenece_al_usuario = (
            partida_existente.paciente.profesional_id == request.user.id
            if perfil.rol == "profesional"
            else partida_existente.paciente.user_id == request.user.id
        )

        if not pertenece_al_usuario:
            return Response(
                {"error": "No tienes permisos para acceder a esta partida."},
                status=status.HTTP_409_CONFLICT
            )

        if partida_existente.request_hash != request_hash:
            return Response(
                {
                    "error": (
                        "La clave de idempotencia ya fue utilizada "
                        "con datos diferentes."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        return Response(
            {
                "mensaje": "La partida ya había sido registrada.",
                "indicador_rendimiento": partida_existente.estado_cognitivo,
                "paciente": partida_existente.paciente.codigo_publico,
            },
            status=status.HTTP_200_OK
        )

    try:
        resultado = predecir_rendimiento(
            juego=datos_validados["juego"],
            puntaje=datos_validados["puntaje"],
            tiempo_total=datos_validados["tiempo_total"],
            fallos=datos_validados["fallos"],
            dificultad=datos_validados["dificultad"],
            nivel_maximo=datos_validados["nivel_maximo"],
            reaccion=datos_validados["reaccion"],
        )

        indicador = resultado["indicador"]

    except Exception:
        logger.exception("Error al calcular indicador de rendimiento")
        indicador = "Sin datos"

    try:
        with transaction.atomic():
            if perfil.rol == "profesional":
                paciente_instancia, _ = Paciente.objects.get_or_create(
                    profesional=request.user,
                    institucion=institucion,
                    pseudonimo_hash=pseudonimo_hash,
                )

            partida = serializer.save(
                paciente=paciente_instancia,
                estado_cognitivo=indicador,
                request_hash=request_hash,
            )

    except IntegrityError:
        partida_existente = Partida.objects.select_related(
            "paciente"
        ).filter(
            idempotency_key=idempotency_key
        ).first()

        if not partida_existente:
            raise

        pertenece_al_usuario = (
            partida_existente.paciente.profesional_id == request.user.id
            if perfil.rol == "profesional"
            else partida_existente.paciente.user_id == request.user.id
            )

        if not pertenece_al_usuario:
            return Response(
                {"error": "No tienes permisos para acceder a esta partida."},
                status=status.HTTP_409_CONFLICT
            )

        if partida_existente.request_hash != request_hash:
            return Response(
                {
                    "error": (
                        "La clave de idempotencia ya fue utilizada "
                        "con datos diferentes."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        return Response(
            {
                "mensaje": "La partida ya había sido registrada.",
                "indicador_rendimiento": partida_existente.estado_cognitivo,
                "paciente": partida_existente.paciente.codigo_publico,
            },
            status=status.HTTP_200_OK
        )
        
    return Response(
        {
            "mensaje": "Éxito",
            "indicador_rendimiento": indicador,
            "paciente": paciente_instancia.codigo_publico,
        },
        status=status.HTTP_201_CREATED
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key="user", rate="5/10m", method="POST", block=False)
def analisis(request):
    if getattr(request, "limited", False):
        return Response(
            {
                "error": (
                    "Has realizado demasiadas solicitudes de análisis. "
                    "Intenta nuevamente más tarde."
                )
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    try:
        perfil = Perfiles.objects.get(user=request.user)
    except Perfiles.DoesNotExist:
         return Response(
            {"error": "No tienes un perfil asociado."},
            status=status.HTTP_403_FORBIDDEN
        )

    if perfil.rol != "profesional":
        return Response(
            {"error": "No tienes permisos para generar análisis."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        perfil = Perfiles.objects.get(user=request.user)
        institucion = perfil.institucion
        
        if perfil.modalidad == "institucion" and perfil.institucion is None:
            return Response(
                {"error": "Tu perfil institucional no tiene una institución asociada."},
                status=status.HTTP_403_FORBIDDEN
            )

        partidas = Partida.objects.filter(paciente__profesional=request.user).order_by('paciente__codigo_publico', 'fecha')
        
        from collections import defaultdict
        datos_pacientes = defaultdict(list)

        MIN_SESIONES = 3
        
        for p in partidas:
            reaccion = None

            if p.tiempo_reaccion_promedio is not None:
                try:
                    reaccion_texto = (
                        str(p.tiempo_reaccion_promedio)
                        .replace("s", "")
                        .replace(",", ".")
                        .strip()
                    )

                    if reaccion_texto:
                        valor = float(reaccion_texto)

                        if math.isfinite(valor) and valor > 0:
                            reaccion = valor

                except (TypeError, ValueError):
                    pass

            clave = (
                p.paciente.codigo_publico,
                p.juego,
            )
            
            datos_pacientes[clave].append({
                "fallos": p.fallos,
                "reaccion": reaccion,
                "dificultad": p.nivel_dificultad,
                "fecha": p.fecha.strftime("%d/%m/%Y"),
            })
        datos_validos = {
            clave: sesiones
            for clave, sesiones in datos_pacientes.items()
            if len(sesiones) >= MIN_SESIONES
        }
        resumen = ""

        for indice, ((codigo, juego), sesiones) in enumerate(
            datos_validos.items(),
            start=1
        ):
            resumen += (
                f"\nPaciente {indice} | Código: {codigo} | "
                f"Juego: {juego} | "
                f"{len(sesiones)} sesiones\n"
            )

            for s in sesiones[-5:]:
                reaccion = (
                    f"{s['reaccion']:.2f}s"
                    if s["reaccion"] is not None
                    else "N/D"
                )

                resumen += (
                    f"- {s['fecha']} | "
                    f"Fallos: {s['fallos']} | "
                    f"Reacción: {reaccion} | "
                    f"Dificultad: {s['dificultad']}\n"
                )
        
        if not datos_validos:
            return Response(
                {"error": ("No hay pacientes con al menos 3 sesiones " "para generar un análisis fiable")},
                status=status.HTTP_400_BAD_REQUEST
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
                    Si una métrica aparece N/D o no está disponible, no la interpretes ni las reemplaces por cero.
                    No uses tablas Markdown.
                    Evita repetir los datos innecesariamente.
                    
                    Datos:
                    {resumen}"""
                        }]
                    )

        return Response({
        'analisis': message.choices[0].message.content
        }, status=status.HTTP_200_OK)
    
    except Perfiles.DoesNotExist:
        return Response(
            {"error": "No tienes un perfil asociado a una institución."},
            status=status.HTTP_403_FORBIDDEN
        )
        
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