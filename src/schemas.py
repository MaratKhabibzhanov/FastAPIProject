from typing import Annotated, Optional

from fastapi import HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, field_validator

from src.models.models import MINIMUM_APP_VERSION


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int | None = Field(ge=0)
    is_subscribed: bool | None


class Contact(BaseModel):
    email: EmailStr
    phone: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> Optional[str]:
        if not value:
            return None
        if not value.isdigit() or len(value) < 7 or len(value) > 15:
            raise ValueError("Invalid phone number")
        return value


class Feedback(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    message: str = Field(min_length=10, max_length=500)
    contact: Contact

    @field_validator("message", mode="after")
    @classmethod
    def censor(cls, value: str) -> str:
        if any(word in value for word in ("редис", "бяк", "козявк")):
            raise ValueError("Value error, Использование недопустимых слов")
        return value


class CommonHeaders(BaseModel):
    user_agent: str | None = None
    accept_language: str | None = None
    x_current_version: Annotated[str, Query(..., regex=r"^\d+\.\d+\.\d+$", example=MINIMUM_APP_VERSION)]

    @field_validator("accept_language", mode="after")
    @classmethod
    def lang_validator(cls, value: str) -> str:
        if not value:
            raise HTTPException(status_code=400, detail="Accept-Language header required")
        if value != "en-CA,en-US;q=0.7,en;q=0.3":
            raise ValueError("Не корректные данные")
        return value

    @field_validator("user_agent", mode="after")
    @classmethod
    def user_agent_validator(cls, value: str) -> str:
        if not value:
            raise HTTPException(status_code=400, detail="User-Agent header required")
        return value

    @field_validator("x_current_version", mode="after")
    @classmethod
    def x_current_version_validator(cls, value: str) -> str:
        if value == MINIMUM_APP_VERSION:
            return value
        for s, o in zip(value.split("."), MINIMUM_APP_VERSION.split(".")):
            if s == o:
                continue
            if s > o:
                return value
        raise ValueError("Требуется обновить приложение")
