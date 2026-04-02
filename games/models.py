from django.db import models
from django.contrib.auth.models import User

class Institucion(models.Model):
    nombre = models.CharField(max_length=180)

class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nickname = models.CharField(max_length=50, unique=True)
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nickname
    
class Partida(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    juego = models.CharField(max_length=20)
    puntaje = models.IntegerField()
    tiempo = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    fallos = models.IntegerField(default=0)
    nivel_dificultad = models.CharField(max_length=20, default="basico")
    nivel_maximo_alcanzado = models.IntegerField(default=0)
    tiempo_reaccion_promedio = models.FloatField(default= 0.0)

class Perfiles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Medico de {self.institucion.nombre}"