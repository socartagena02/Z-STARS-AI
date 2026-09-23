from rest_framework import serializers
from .models import Partida

class PartidaSerializers(serializers.ModelSerializer):
    paciente_code = serializers.ReadOnlyField(
        source='paciente.codigo_publico'
    )

    class Meta:
        model = Partida
        fields = ['id', 
                  'juego', 
                  'puntaje', 
                  'tiempo', 
                  'fecha', 
                  'fallos', 
                  'paciente_code',
                  'nivel_dificultad', 
                  'nivel_maximo_alcanzado',
                  'tiempo_reaccion_promedio']