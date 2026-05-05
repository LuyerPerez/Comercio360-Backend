from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import decode_access_token
from schemas.user_schema import UserCreate, UserResponse, UserUpdate
from services.user_service import (
    create_user,
    email_exists,
    get_user_by_email,
    get_user_by_id,
    get_users,
    phone_exists,
    set_user_active,
    update_user,
)
from models.role_model import UserRole

router = APIRouter(prefix="/api/inventory/users", tags=["Usuarios"])
bearer_scheme = HTTPBearer(auto_error=False)

ADMIN_ROLES = {UserRole.OWNER, UserRole.ADMIN}

def _get_authenticated_user(
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

def require_admin_or_owner(
    current_user: UserResponse = Depends(_get_authenticated_user),
) -> UserResponse:
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta accion. Se requiere rol owner o admin.",
        )
    return current_user

@router.post(
    "/create",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    description="Crea un nuevo usuario en el sistema con email y telefono unicos.",
)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    if email_exists(db, user_data.email.lower()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este correo",
        )

    if user_data.phone is not None and phone_exists(db, user_data.phone):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este telefono",
        )

    return UserResponse.model_validate(create_user(db, user_data))

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario autenticado",
    description="Retorna los datos del usuario que inicio sesion usando el token actual.",
)
def get_current_user(
    current_user: UserResponse = Depends(_get_authenticated_user),
) -> UserResponse:
    return current_user

@router.patch(
    "/update/me",
    response_model=UserResponse,
    summary="Actualizar usuario autenticado",
    description="Actualiza los datos del usuario autenticado. No permite cambiar role ni is_active.",
)
def update_current_user(
    user_data: UserUpdate,
    current_user: UserResponse = Depends(_get_authenticated_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    if user_data.role is not None or user_data.is_active is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes cambiar role o is_active desde este endpoint.",
        )

    if user_data.email is not None and email_exists(db, user_data.email.lower(), exclude_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este correo",
        )

    if user_data.phone is not None and phone_exists(db, user_data.phone, exclude_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este telefono",
        )

    user = get_user_by_id(db, current_user.id)
    return UserResponse.model_validate(update_user(db, user, user_data))

@router.get(
    "",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Lista usuarios con filtros opcionales. Requiere rol owner o admin.",
)
def list_users_endpoint(
    search: str | None = Query(default=None, min_length=2, max_length=100),
    role: UserRole | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: UserResponse = Depends(require_admin_or_owner),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    return [UserResponse.model_validate(u) for u in get_users(db, skip=skip, limit=limit, search=search, role=role, is_active=is_active)]

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por ID",
    description="Retorna los datos de un usuario por su ID. Requiere rol owner o admin.",
)
def get_user_by_id_endpoint(
    user_id: int,
    current_user: UserResponse = Depends(require_admin_or_owner),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return UserResponse.model_validate(user)

@router.patch(
    "/update/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario por ID",
    description="Permite actualizar cualquier usuario por su ID. Requiere rol owner o admin.",
)
def update_user_by_id(
    user_id: int,
    user_data: UserUpdate,
    current_user: UserResponse = Depends(require_admin_or_owner),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if user_data.email is not None and email_exists(db, user_data.email.lower(), exclude_id=user_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un usuario con este correo")

    if user_data.phone is not None and phone_exists(db, user_data.phone, exclude_id=user_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un usuario con este telefono")

    return UserResponse.model_validate(update_user(db, user, user_data))

@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activar usuario por ID",
    description="Activa un usuario desactivado. Requiere rol owner o admin.",
)
def activate_user_by_id(
    user_id: int,
    current_user: UserResponse = Depends(require_admin_or_owner),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return UserResponse.model_validate(set_user_active(db, user, True))

@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Desactivar usuario por ID",
    description="Desactiva un usuario activo. Requiere rol owner o admin.",
)
def deactivate_user_by_id(
    user_id: int,
    current_user: UserResponse = Depends(require_admin_or_owner),
    db: Session = Depends(get_db),
) -> UserResponse:
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes desactivarte a ti mismo.")
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return UserResponse.model_validate(set_user_active(db, user, False))
