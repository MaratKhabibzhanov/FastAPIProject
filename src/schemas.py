from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


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
