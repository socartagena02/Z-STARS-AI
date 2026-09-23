from django.contrib import admin
from .models import Paciente, Partida, Institucion, Perfiles, Consentimiento

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_publico", 
        "institucion", 
        "profesional", 
    )
    search_fields = ("codigo_publico",)
    list_filter = ("institucion",)
    
admin.site.register(Perfiles)
admin.site.register(Partida)
admin.site.register(Institucion)
admin.site.register(Consentimiento)