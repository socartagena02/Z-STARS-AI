from rest_framework import serializers
from .models import Partida

class PartidaSerializers(serializers.ModelSerializer):
    paciente_nickname = serializers.ReadOnlyField(source='paciente.nickname')

    class Meta:
        model = Partida
        fields = ['id', 
                  'juego', 
                  'puntaje', 
                  'tiempo', 
                  'fecha', 
                  'fallos', 
                  'paciente_nickname',
                  'nivel_dificultad', 
                  'nivel_maximo_alcanzado',
                  'tiempo_reaccion_promedio']