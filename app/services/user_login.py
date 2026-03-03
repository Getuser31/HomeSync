from sqlalchemy.orm import Session
from ..auth import create_access_token
from passlib.context import CryptContext

from ..models import User


def login_user(db: Session, email: str, password: str) -> str | None:
    user = db.query(User).filter(User.email == email).first()
    pwd_context = CryptContext(schemes=["bcrypt"])
    if user and pwd_context.verify(password, user.hashed_password):
        return create_access_token(user.id, user.email)
    return None
