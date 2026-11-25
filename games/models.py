import secrets 
import string
import hashlib

from django.db import models, transaction, IntegrityError
from django.conf import settings
from .security import(encrypt_secret, decrypt_secret)
from django.utils import timezone
from django.db.models import Q

class Vinculacion(models.Model):
    ESTADOS = [
        ('activa', 'Activa'),
        ('desvinculada', 'Desvinculada'),
    ]

    paciente = models.ForeignKey(
        'games.Perfiles',
        on_delete=models.PROTECT,
        related_name='vinculaciones_como_paciente',
    )

    profesional = models.ForeignKey(
        'games.Perfiles',
        on_delete=models.PROTECT,
        related_name='vinculaciones_como_profesional',
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='activa',
    )

    fecha_vinculacion = models.DateTimeField(
        default=timezone.now
    )

    fecha_desvinculacion = models.DateTimeField(
        null=True,
        blank=True,
    )

    desvinculado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vinculaciones_desvinculadas',
    )

    class Meta:
        ordering = ['-fecha_vinculacion']
        constraints = [
            models.UniqueConstraint(
                fields=['paciente', 'profesional'],
                condition=Q(estado='activa'),
                name='unique_vinculacion_activa',
            )
        ]

    def __str__(self):
        return (
            f"{self.paciente} - {self.profesional} "
            f"({self.estado})"
        )

class InvitacionVinculacion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('revocada', 'Revocada'),
        ('expirada', 'Expirada'),
    ]

    profesional = models.ForeignKey(
        'games.Perfiles',
        on_delete=models.PROTECT,
        related_name='invitaciones_vinculacion',
    )

    paciente = models.ForeignKey(
        'games.Perfiles',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='invitaciones_recibidas',
    )

    token_hash = models.CharField(
        max_length=64,
        unique=True,
    )

    estado = models.CharField(
        max_length=28,
        choices=ESTADOS,
        default='pendiente',
    )

    fecha_creacion = models.DateTimeField(
        default=timezone.now,
    )

    fecha_expiracion = models.DateTimeField()

    fecha_respuesta = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return (
            f"Invitación de {self.profesional} "
            f"({self.estado})"
        )

    @staticmethod
    def generar_token():
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(token.encode()).hexdigest()

    @property
    def esta_expirada(self):
        return timezone.now() >= self.fecha_expiracion

    @property
    def puede_utilizarse(self):
        return (
            self.estado == 'pendiente'
            and not self.esta_expirada
        )
    
class TwoFactorAuth (models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="two_factor"
    )
    
    secret_key = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )
    
    pending_secret = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )
    
    last_used_counter = models.BigIntegerField(default=-1)
    
    is_enabled = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def set_pending_secret(self, secret):
        self.pending_secret = encrypt_secret(secret)

    def get_pending_secret(self):
        if not self.pending_secret:
            return None
        
        return decrypt_secret(self.pending_secret)

    def set_secret(self, secret):
        self.secret_key = encrypt_secret(secret)

    def get_secret(self):
        if not self.secret_key:
            return None
        
        return decrypt_secret(self.secret_key)

    def clear_pending_secret(self):
        self.pending_secret = ""
    
    def __str__(self):
        return f"2FA - {self.user.username}"

def generar_code_paciente():
    cat = string.ascii_uppercase + string.digits
    
    return "PAC-" + "".join(
        secrets.choice(cat) for _ in range(6)
    )

class Institucion(models.Model):
    nombre = models.CharField(max_length=180)
    
    def __str__(self):
        return self.nombre
    
class Paciente(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="paciente",
        null=True,
        blank=True,
    )
    
    pseudonimo_hash = models.CharField(max_length=64)

    codigo_publico = models.CharField(
        max_length=10,
        unique=True,
        editable=False
    )

    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        related_name="pacientes",
        null=True,
        blank=True
    )

    profesional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pacientes_asignados",
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profesional", "pseudonimo_hash"],
                name="unique_pseudonimo_por_profesional"
            )
        ]

    def save(self, *args, **kwargs):
        if self.codigo_publico:
            return super().save(*args, **kwargs)

        for _ in range(5):
            self.codigo_publico = generar_code_paciente()
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError:
                if not Paciente.objects.filter(
                    codigo_publico=self.codigo_publico
                ).exists():
                    raise

        raise RuntimeError(
            "No fue posible generar un código único para el paciente."
        )

    def __str__(self):
        return self.codigo_publico
    
class Partida(models.Model):
    paciente = models.ForeignKey(
        Paciente, 
        on_delete=models.PROTECT,
        related_name="partidas"
        )
    juego = models.CharField(max_length=20)
    puntaje = models.IntegerField()
    tiempo = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    fallos = models.IntegerField(default=0)
    nivel_dificultad = models.CharField(
        max_length=20, 
        default="basico"
    )
    nivel_maximo_alcanzado = models.IntegerField(
        null=True,
        blank=True,
        default=None
    )
    tiempo_reaccion_promedio = models.FloatField(
        null=True,
        blank=True,
        default=None
    )
    estado_cognitivo = models.CharField(
        max_length=100, 
        default="Sin datos"
    )
    
    idempotency_key = models.UUIDField(unique=True, editable=False)
    request_hash = models.CharField(
        max_length=64,
        editable=False
    )
    
    def __str__(self):
        return f"{self.paciente.codigo_publico} - {self.juego} - {self.fecha}"
    
class Perfiles(models.Model):
    ROLES = [
        ('paciente', 'Paciente'),
        ('profesional', 'Profesional'),
    ]

    MODALIDADES = [
        ('institucional', 'Institucional'),
        ('independiente', 'Independiente'),
    ]

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        null=True,
        blank=True
    )

    modalidad = models.CharField(
        max_length=20,
        choices=MODALIDADES,
        null=True,
        blank=True
    )

    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfiles'
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        if self.rol == 'paciente':
            return f"Paciente - {self.user.username}"

        if self.modalidad == 'independiente':
            return f"Profesional independiente - {self.user.username}"

        if self.institucion:
            return f"Profesional de {self.institucion.nombre}"

        return f"Perfil - {self.user.username}"
    
class Consentimiento(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consentimientos"
    )

    tipo = models.CharField(max_length=50)
    version = models.CharField(max_length=20)
    otorgado = models.BooleanField(default=False)

    fecha_otorgamiento = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.tipo} - {self.version}"
        )

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    
    def __str__(self):
        return f"Perfil {self.user.username}"