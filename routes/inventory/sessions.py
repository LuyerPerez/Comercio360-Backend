from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth_schema import SessionCreate, TokenResponse
from services.auth_service import create_access_token
from services.user_service import authenticate_user

router = APIRouter(prefix="/api/inventory/sessions", tags=["sessions"])

@router.post("", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_data: SessionCreate, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, session_data.email, session_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    access_token = create_access_token(subject=user.email)
    return TokenResponse(access_token=access_token, token_type="bearer")
