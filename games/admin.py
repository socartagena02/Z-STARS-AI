from django.contrib import admin
from .models import Paciente, Partida, Institucion, Perfiles

admin.site.register(Perfiles)
admin.site.register(Paciente)
admin.site.register(Partida)
admin.site.register(Institucion)