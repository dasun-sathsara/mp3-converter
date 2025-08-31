from datetime import datetime

from pydantic import BaseModel, EmailStr, conint, constr
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[valid-type]

    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: int = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    age: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=8)  # type: ignore[valid-type]
    age: conint(ge=0, le=150)  # type: ignore[valid-type]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ValidateResponse(BaseModel):
    valid: bool
    user_id: int | None = None
    email: EmailStr | None = None

