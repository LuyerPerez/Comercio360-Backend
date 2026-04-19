from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import decode_access_token
from schemas.user_schema import UserCreate, UserResponse
from services.user_service import create_user, get_user_by_email, get_user_by_username

router = APIRouter(prefix="/api/inventory/users", tags=["users"])
bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserResponse:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
        )

    user_email = decode_access_token(credentials.credentials)
    if user_email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        )

    user = get_user_by_email(db, user_email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token no corresponde a un usuario valido",
        )

    return UserResponse.model_validate(user)

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    existing_user = get_user_by_email(db, user_data.email.lower())
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este correo",
        )

    existing_username = get_user_by_username(db, user_data.username.lower())
    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este nombre de usuario",
        )

    user = create_user(db, user_data)
    return UserResponse.model_validate(user)

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user
