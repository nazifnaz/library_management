from enum import Enum
from typing import List

from pydantic import EmailStr
from sqlmodel import SQLModel, Field

from src.borrowings.schemas import BorrowingModel
from src.db.enums import UserRole


class RoleChoices(str, Enum):
    USER = "user"
    LIBRARIAN = "librarian"
    # ADMIN = "admin"


class UserCreateModel(SQLModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: RoleChoices


class UserBorrowingModel(SQLModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    borrowings: List[BorrowingModel]


class UserLoginModel(SQLModel):
    email: EmailStr
    password: str


class EmailModel(SQLModel):
    addresses : List[EmailStr]


class PasswordResetRequestModel(SQLModel):
    email: EmailStr


class PasswordResetConfirmModel(SQLModel):
    new_password: str
    confirm_new_password: str
