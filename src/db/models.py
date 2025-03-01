from datetime import datetime, date
from enum import Enum
from typing import Optional, List

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy.dialects import postgresql as pg

from src.db.enums import UserRole, BoookCopyStatus, BorrowingStatus


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    first_name: str
    last_name: str
    role: UserRole = Field(default=UserRole.USER)
    password_hash: str = Field(sa_column=Column(pg.VARCHAR, nullable=False), exclude=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    borrowings: List["Borrowing"] = Relationship(back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"


class Author(SQLModel, table=True):
    __tablename__ = "authors"

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    birth_date: Optional[date] = None
    death_date: Optional[date] = None

    # Relationships
    books: List["Book"] = Relationship(back_populates="authors")


class Publisher(SQLModel, table=True):
    __tablename__ = "publishers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None

    # Relationships
    books: List["Book"] = Relationship(back_populates="publisher")


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    category_name: str = Field(unique=True, index=True)
    parent_category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    description: Optional[str] = None

    # Relationships
    subcategories: List["Category"] = Relationship(back_populates="parent_category")
    parent_category: Optional["Category"] = Relationship(back_populates="subcategories")
    books: List["Book"] = Relationship(back_populates="categories")


class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: Optional[int] = Field(default=None, primary_key=True)
    isbn: str = Field(unique=True, index=True)
    title: str = Field(index=True)
    publisher_id: Optional[int] = Field(default=None, foreign_key="publishers.id")
    publication_date: Optional[date] = None
    edition: Optional[str] = None
    language: str = "English"
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    publisher: Optional[Publisher] = Relationship(back_populates="books")
    categories: List[Category] = Relationship(back_populates="books")
    authors: List[Author] = Relationship(back_populates="books")
    book_copies: List["BookCopy"] = Relationship(back_populates="book")


class BookCopy(SQLModel, table=True):
    __tablename__ = "book_copies"

    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id", index=True)
    copy_number: str
    acquisition_date: Optional[date] = None
    price: Optional[float] = None
    status: BoookCopyStatus = Field(default=BoookCopyStatus.AVAILABLE, sa_column=Column(pg.VARCHAR(20)))
    location: Optional[str] = None
    condition: Optional[str] = None
    notes: Optional[str] = None

    # Relationships
    book: Book = Relationship(back_populates="book_copies")
    borrowings: List["Borrowing"] = Relationship(back_populates="book_copy")


class Borrowing(SQLModel, table=True):
    __tablename__ = "borrowings"

    id: Optional[int] = Field(default=None, primary_key=True)
    copy_id: int = Field(foreign_key="book_copies.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    borrowed_date: datetime = Field(default_factory=datetime.now)
    due_date: datetime
    returned_date: Optional[datetime] = None
    extended_times: int = 0
    status: BorrowingStatus = Field(default=BorrowingStatus.ACTIVE)
    notes: Optional[str] = None
    created_by: int = Field(foreign_key="users.id")  # Librarian ID

    # Relationships
    user: User = Relationship(back_populates="borrowings")
    book_copy: BookCopy = Relationship(back_populates="borrowings")

