from django.contrib import admin
from .models import Paciente, Partida, Institucion, Perfiles, Consentimiento

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'institucion', 'profesional')
    list_filter = ('institucion', 'profesional')
    search_fields = ('nickname',)
    
admin.site.register(Perfiles)
admin.site.register(Partida)
admin.site.register(Institucion)
admin.site.register(Consentimiento)