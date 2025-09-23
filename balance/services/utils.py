import jwt
from config.config import settings

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_kEY, algorithms=[settings.JWT_ALGHORITM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


