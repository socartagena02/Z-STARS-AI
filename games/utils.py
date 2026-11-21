import hmac
import hashlib
import unicodedata

from django.conf import settings


def pseudonimizar_nickname(nickname, profesional_id, institucion_id=None):
    nickname_normalizado = unicodedata.normalize(
        "NFC",
        nickname.strip().casefold()
    )

    institucion_scope = (
        str(institucion_id)
        if institucion_id is not None
        else "independiente"
    )

    texto = (
        f"{institucion_scope}:"
        f"{profesional_id}:"
        f"{nickname_normalizado}"
    )

    return hmac.new(
        settings.PSEUDONYM_KEY.encode("utf-8"),
        texto.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()