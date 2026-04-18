from datetime import datetime
from sqlalchemy.orm import Session
from inventory_api.models.user_model import User
from inventory_api.schemas.user_schema import UserCreate
from inventory_api.services.auth_service import hash_password, verify_password

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        email=user_data.email.lower(),
        username=user_data.username.lower(),
        full_name=user_data.full_name,
        role=user_data.role,
        password_hash=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email.lower())
    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    user.last_login_at = datetime.utcnow()
    db.commit()

    return user
