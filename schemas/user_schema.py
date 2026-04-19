from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=2, max_length=255)
    role: Literal["owner", "admin", "manager", "cashier", "staff"] = "staff"
    password: str = Field(min_length=8, max_length=128)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    full_name: str
    role: str
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime
