from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import Session
from models.user_model import User
from models.role_model import UserRole
from schemas.user_schema import UserCreate, UserUpdate
from services.auth_service import hash_password, verify_password

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_phone(db: Session, phone: str) -> User | None:
    return db.query(User).filter(User.phone == phone).first()

def email_exists(db: Session, email: str, exclude_id: int | None = None) -> bool:
    query = db.query(User).filter(User.email == email)
    if exclude_id is not None:
        query = query.filter(User.id != exclude_id)
    return query.first() is not None

def phone_exists(db: Session, phone: str, exclude_id: int | None = None) -> bool:
    query = db.query(User).filter(User.phone == phone)
    if exclude_id is not None:
        query = query.filter(User.id != exclude_id)
    return query.first() is not None

def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: str | None = None,
    role: UserRole | None = None,
    is_active: bool | None = None,
) -> list[User]:
    query = db.query(User)

    if search is not None and search.strip():
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.firstname.ilike(search_term),
                User.firstlastname.ilike(search_term),
                User.email.ilike(search_term),
            )
        )

    if role is not None:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.order_by(User.id.desc()).offset(skip).limit(limit).all()

def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        firstname=user_data.firstname,
        secondname=user_data.secondname,
        firstlastname=user_data.firstlastname,
        secondlastname=user_data.secondlastname,
        email=user_data.email.lower(),
        phone=user_data.phone,
        role=user_data.role,
        password_hash=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user: User, user_data: UserUpdate) -> User:
    if user_data.firstname is not None:
        user.firstname = user_data.firstname

    if user_data.secondname is not None:
        user.secondname = user_data.secondname

    if user_data.firstlastname is not None:
        user.firstlastname = user_data.firstlastname

    if user_data.secondlastname is not None:
        user.secondlastname = user_data.secondlastname

    if user_data.email is not None:
        user.email = user_data.email.lower()

    if user_data.phone is not None:
        user.phone = user_data.phone

    if user_data.role is not None:
        user.role = user_data.role

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)

    db.commit()
    db.refresh(user)
    return user

def set_user_active(db: Session, user: User, is_active: bool) -> User:
    user.is_active = is_active
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
