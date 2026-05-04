from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Perfiles, Institucion

@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        institucion_default, _ = Institucion.objects.get_or_create(
            nombre="Sin Institución Asignada"
        )
        Perfiles.objects.create(user=instance, institucion=institucion_default)