import hmac
import hashlib

from django.conf import settings


def pseudonimizar_nickname(nickname, profesional_id, institucion_id):
    nickname_normalizado = nickname.strip().casefold()

    texto = (
        f"{institucion_id}:"
        f"{profesional_id}:"
        f"{nickname_normalizado}"
    )

    return hmac.new(
        settings.PSEUDONYM_KEY.encode("utf-8"),
        texto.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()