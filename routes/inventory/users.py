from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import decode_access_token
from schemas.user_schema import UserCreate, UserResponse, UserUpdate
from services.user_service import create_user, get_user_by_email, get_user_by_id, get_user_by_phone, update_user

router = APIRouter(prefix="/api/inventory/users", tags=["Usuarios"])
bearer_scheme = HTTPBearer(auto_error=False)

@router.post(
    "/create",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    description="Crea un nuevo usuario en el sistema con email y telefono unicos.",
)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    existing_user = get_user_by_email(db, user_data.email.lower())
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este correo",
        )

    existing_phone = get_user_by_phone(db, user_data.phone)
    if existing_phone is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este telefono",
        )

    user = create_user(db, user_data)
    return UserResponse.model_validate(user)

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario autenticado",
    description="Retorna los datos del usuario que inicio sesion usando el token actual.",
)
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

@router.patch(
    "/update/me",
    response_model=UserResponse,
    summary="Actualizar usuario autenticado",
    description="Actualiza los datos del usuario que tiene la sesion activa.",
)
def update_current_user(
    user_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = get_user_by_email(db, current_user.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    if user_data.email is not None and user_data.email.lower() != user.email:
        existing_user = get_user_by_email(db, user_data.email.lower())
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con este correo",
            )

    if user_data.phone is not None and user_data.phone != user.phone:
        existing_phone = get_user_by_phone(db, user_data.phone)
        if existing_phone is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con este telefono",
            )

    updated_user = update_user(db, user, user_data)
    return UserResponse.model_validate(updated_user)


@router.patch(
    "/update/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario por ID",
    description="Permite actualizar cualquier usuario por su ID. Solo debe usarse desde flujos administrativos.",
)
def update_user_by_id(
    user_id: int,
    user_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    if user_data.email is not None and user_data.email.lower() != user.email:
        existing_user = get_user_by_email(db, user_data.email.lower())
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con este correo",
            )

    if user_data.phone is not None and user_data.phone != user.phone:
        existing_phone = get_user_by_phone(db, user_data.phone)
        if existing_phone is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con este telefono",
            )

    updated_user = update_user(db, user, user_data)
    return UserResponse.model_validate(updated_user)
