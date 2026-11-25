from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction, IntegrityError

from games.models import Perfiles, InvitacionVinculacion, Vinculacion


def validar_perfil_profesional(perfil):
    if perfil is None:
        raise ValidationError(
            'No se encontró tu perfil.'
        )

    if perfil.rol != 'profesional':
        raise ValidationError(
            'Solo un profesional puede realizar esta acción.'
        )


def validar_perfil_paciente(perfil):
    if perfil is None:
        raise ValidationError(
            'No se encontró tu perfil.'
        )

    if perfil.rol != 'paciente':
        raise ValidationError(
            'La vinculación solo puede realizarse con un paciente.'
        )


def crear_invitacion(user):
    perfil = Perfiles.objects.filter(user=user).first()

    validar_perfil_profesional(perfil)

    token = InvitacionVinculacion.generar_token()

    invitacion = InvitacionVinculacion.objects.create(
        profesional=perfil,
        token_hash=InvitacionVinculacion.hash_token(token),
        fecha_expiracion=timezone.now() + timedelta(hours=24)
    )

    return invitacion, token


def validar_aceptacion(perfil_paciente, invitacion):
    validar_perfil_paciente(perfil_paciente)

    if not invitacion.puede_utilizarse:
        raise ValidationError(
            'La invitación no es válida o ha expirado.'
        )

    if invitacion.profesional.rol != 'profesional':
        raise ValidationError(
            'El perfil que generó la invitación no es profesional.'
        )

    if invitacion.profesional.user == perfil_paciente.user:
        raise ValidationError(
            'No puedes vincularte contigo mismo.'
        )

@transaction.atomic
def aceptar_invitacion(perfil_paciente, token):
    validar_perfil_paciente(perfil_paciente)

    token_hash = InvitacionVinculacion.hash_token(token)

    invitacion = (
        InvitacionVinculacion.objects
        .select_for_update()
        .filter(token_hash=token_hash)
        .first()
    )

    if invitacion is None:
        raise ValidationError(
            'La invitación no existe o el código es incorrecto.'
        )

    validar_aceptacion(perfil_paciente, invitacion)

    if Vinculacion.objects.filter(
        paciente=perfil_paciente,
        profesional=invitacion.profesional,
        estado='activa'
    ).exists():
        raise ValidationError(
            'Ya existe una vinculación activa con este profesional.'
        )

    try:
        with transaction.atomic():
            vinculacion = Vinculacion.objects.create(
                paciente=perfil_paciente,
                profesional=invitacion.profesional,
                estado='activa'
            )
    except IntegrityError:
        raise ValidationError(
            'Ya existe una vinculación activa con este profesional.'
        )

    invitacion.paciente = perfil_paciente
    invitacion.estado = 'aceptada'
    invitacion.fecha_respuesta = timezone.now()

    invitacion.save(
        update_fields=[
            'paciente',
            'estado',
            'fecha_respuesta'
        ]
    )

    return vinculacion

@transaction.atomic
def desvincular(vinculacion, user):
    perfil_profesional = Perfiles.objects.filter(
        user=user
    ).first()

    validar_perfil_profesional(perfil_profesional)

    vinculacion = (
        Vinculacion.objects
        .select_for_update()
        .filter(pk=vinculacion.pk)
        .first()
    )

    if vinculacion is None:
        raise ValidationError(
            'La vinculación no existe.'
        )

    if vinculacion.profesional != perfil_profesional:
        raise ValidationError(
            'No tienes permiso para desvincular a este paciente.'
        )

    if vinculacion.estado != 'activa':
        raise ValidationError(
            'Esta vinculación ya está desvinculada.'
        )

    vinculacion.estado = 'desvinculada'
    vinculacion.fecha_desvinculacion = timezone.now()
    vinculacion.desvinculado_por = user

    vinculacion.save(
        update_fields=[
            'estado',
            'fecha_desvinculacion',
            'desvinculado_por'
        ]
    )

    return vinculacion