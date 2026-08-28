import hashlib
import hmac
import os
import secrets
import string

from django.db import migrations


def generar_code(Paciente):
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


def pseudonimizar(nickname, profesional_id):
    key = os.environ["PSEUDONYM_KEY"]

    nickname_normal = nickname.strip().casefold()
    text = f"{profesional_id}:{nickname_normal}"

    return hmac.new(
        key.encode("utf-8"),
        text.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def backfill_pacientes(apps, schema_editor):
    Paciente = apps.get_model("games", "Paciente")

    for paciente in Paciente.objects.all():
        campos_act = []

        if not paciente.codigo_publico:
            paciente.codigo_publico = generar_code(Paciente)
            campos_act.append("codigo_publico")

        if (
            paciente.nickname
            and paciente.profesional_id
            and not paciente.pseudonimo_hash
        ):
            paciente.pseudonimo_hash = pseudonimizar(
                paciente.nickname,
                paciente.profesional_id
            )
            campos_act.append("pseudonimo_hash")

        if campos_act:
            paciente.save(update_fields=campos_act)


class Migration(migrations.Migration):

    dependencies = [
        (
            "games",
            "0011_remove_paciente_unique_nickname_por_profesional_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            backfill_pacientes,
            migrations.RunPython.noop,
        ),
    ]