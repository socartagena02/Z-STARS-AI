
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def get_fernet():
    key = getattr(settings, "TWO_FACTOR_KEY", None)

    if not key:
        raise RuntimeError(
            "TWO_FACTOR_KEY no está configurada."
        )

    try:
        if isinstance(key, str):
            key = key.encode("utf-8")

        return Fernet(key)

    except (ValueError, TypeError):
        raise RuntimeError(
            "TWO_FACTOR_KEY no es válida."
        )


def encrypt_secret(secret):
    if not secret:
        return ""

    fernet = get_fernet()

    return fernet.encrypt(
        secret.encode("utf-8")
    ).decode("utf-8")


def decrypt_secret(encrypted_secret):
    if not encrypted_secret:
        return ""

    fernet = get_fernet()

    try:
        return fernet.decrypt(
            encrypted_secret.encode("utf-8")
        ).decode("utf-8")

    except (InvalidToken, ValueError, TypeError):
        raise RuntimeError(
            "No fue posible descifrar el secreto 2FA."
        )
