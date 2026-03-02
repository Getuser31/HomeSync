import secrets
import string

from sqlalchemy.orm import Session

from ..models import House


def _generate_invite_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_unique_invite_code(db: Session, length: int = 8) -> str:
    while True:
        code = _generate_invite_code(length)
        if not db.query(House).filter(House.invite_code == code).first():
            return code
