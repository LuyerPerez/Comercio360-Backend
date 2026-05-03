from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from models.role_model import UserRole

class UserCreate(BaseModel):
    firstname: str = Field(min_length=2, max_length=100)
    secondname: str | None = Field(default=None, min_length=2, max_length=100)
    firstlastname: str = Field(min_length=2, max_length=100)
    secondlastname: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, min_length=7, max_length=20)
    role: UserRole = UserRole.STAFF
    password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="before")
    @classmethod
    def normalize_optional_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        for field_name in ("secondname", "secondlastname", "phone"):
            field_value = data.get(field_name)
            if isinstance(field_value, str) and field_value.strip() == "":
                data[field_name] = None

        return data

class UserUpdate(BaseModel):
    firstname: str | None = Field(default=None, min_length=2, max_length=100)
    secondname: str | None = Field(default=None, min_length=2, max_length=100)
    firstlastname: str | None = Field(default=None, min_length=2, max_length=100)
    secondlastname: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=20)
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)

    @model_validator(mode="before")
    @classmethod
    def normalize_optional_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        for field_name in ("secondname", "secondlastname", "phone"):
            field_value = data.get(field_name)
            if isinstance(field_value, str) and field_value.strip() == "":
                data[field_name] = None

        return data

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    firstname: str
    secondname: str | None
    firstlastname: str
    secondlastname: str | None
    email: EmailStr
    phone: str | None
    role: UserRole
    is_active: bool
    last_login_at: datetime | None
    create_at: datetime
    update_at: datetime
