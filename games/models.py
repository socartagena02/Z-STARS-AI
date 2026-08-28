from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import secrets 
import string

def generar_code_paciente():
    cat = string.ascii_uppercase + string.digits
    
    while True:
        codigo = "PAC-" + "".join(
            secrets.choice(cat)
            for _ in range(6)
        )
        
        if not Paciente.objects.filter(
            codigo_publico=codigo
        ).exists():
            return codigo

class Institucion(models.Model):
    nombre = models.CharField(max_length=180)
    
    def __str__(self):
        return self.nombre
    
class Paciente(models.Model):
    # Campos antiguos
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nickname = models.CharField(User, unique=True, null=True, blank=True)
    
    # Campos nuevos
    pseudonimo_hash =  models.CharField(max_length=64, null=True, blank=True)
    codigo_publico = models.CharField(
        max_length=10, 
        unique=True, 
        null=True,
        blank=True,
        editable=False
    )
    
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE)
    profesional = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        related_name="pacientes_asignados"
    )
    
    class Meta:
        constraints =[
            models.UniqueConstraint(
                fields=["profesional", "pseudonimo_hash"],
                name="unique_pseudonimo_por_profesional"
            )
        ]
    
    def save(self, *args, **kwargs):
        if not self.codigo_publico:
            self.codigo_publico = generar_code_paciente()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.codigo_publico
    
    
class Partida(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    juego = models.CharField(max_length=20)
    puntaje = models.IntegerField()
    tiempo = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    fallos = models.IntegerField(default=0)
    nivel_dificultad = models.CharField(max_length=20, default="basico")
    nivel_maximo_alcanzado = models.IntegerField(default=0)
    tiempo_reaccion_promedio = models.FloatField(
        null=True,
        blank=True,
        default=None
    )
    estado_cognitivo = models.CharField(max_length=100, default="Sin datos")

class Perfiles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Medico de {self.institucion.nombre}"
    
class Consentimiento(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consentimientos')
    tipo = models.CharField(max_length=50)
    version = models.CharField(max_length=20)
    otorgado = models.BooleanField(default=False)
    fase_otorgamiento = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.tipo} - {self.version}"
