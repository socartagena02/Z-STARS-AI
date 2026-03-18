from django.contrib import admin
from .models import Institucion, Paciente, Partida

admin.site.register(Institucion)
admin.site.register(Paciente)
admin.site.register(Partida)