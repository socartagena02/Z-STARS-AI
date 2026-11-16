
from rest_framework import serializers
from .models import Partida


class PartidaSerializers(serializers.ModelSerializer):
    paciente_code = serializers.ReadOnlyField(
        source="paciente.codigo_publico"
    )

    idempotency_key = serializers.UUIDField(
        write_only=True,
        required=True,
        validators=[]
    )

    class Meta:
        model = Partida
        fields = [
            "id",
            "juego",
            "puntaje",
            "tiempo",
            "fecha",
            "fallos",
            "paciente_code",
            "nivel_dificultad",
            "nivel_maximo_alcanzado",
            "tiempo_reaccion_promedio",
            "idempotency_key",
        ]

        read_only_fields = [
            "id",
            "fecha",
            "paciente_code",
        ]
