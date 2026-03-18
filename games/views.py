from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Paciente, Partida, Institucion, Perfiles
from .serializers import PartidaSerializers
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout

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
        
        partidas_filtradas = Partida.objects.all().order_by('-fecha')
        
        return render(request, "games/dashboard.html", {
            'datos_tabla': partidas_filtradas,
            'institucion': institucion,
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
        "Nombre_web": "MemoryFlow",
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
        return Response({"error": "No hay apodo"}, status=status.HTTP_400_BAD_REQUEST)

    inst, _ = Institucion.objects.get_or_create(nombre="Hospital General")
    paciente_instancia, _ = Paciente.objects.get_or_create(
        nickname__iexact=nickname_recibido,
        defaults={'nickname': nickname_recibido, 'institucion': inst}
    )

    serializer = PartidaSerializers(data=request.data)
    
    if serializer.is_valid():
        serializer.save(paciente=paciente_instancia)
        return Response({"mensaje": "Éxito"}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def logout(request):
    django_logout(request)
    return redirect('iniciosesion')