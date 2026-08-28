import hmac 
import hashlib
from django.conf import settings

def pseudonimizar_nickname(nickname, profesional_id):
    nickname_normalizado = nickname.strip().casefold()
    
    text = f"{profesional_id}:{nickname_normalizado}"
    
    return hmac.new(
        settings.PSEUDONYM_KEY.encode("utf-8"),
        text.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()