from datetime import datetime, timedelta
from jose import jwt, ExpiredSignatureError
from config import SECRET_KEY

SECRET_KEY = SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def decode_access_token(token: str) -> tuple[int | None, bool]:
    """Returns (user_id, token_expired). token_expired is True only when the token was valid but has expired."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"]), False
    except ExpiredSignatureError:
        return None, True
    except Exception:
        return None, False


def create_access_token(user_id: int, email: str, remember_me: bool = False) -> str:
    expire_minutes = 60 * 24 * 365 if remember_me else ACCESS_TOKEN_EXPIRE_MINUTES

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=expire_minutes)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
