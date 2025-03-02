from datetime import datetime, date
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
    is_active: bool = Field(default=True)
    password_hash: str = Field(sa_column=Column(pg.VARCHAR, nullable=False), exclude=True)
    created_at: datetime = Field(default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP, nullable=False))
    updated_at: datetime = Field(default_factory=datetime.now,
                                 sa_column=Column(pg.TIMESTAMP, nullable=False, onupdate=datetime.now))

    # Relationships
    borrowings: List["Borrowing"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin", "foreign_keys": "[Borrowing.user_id]"})
    api_keys: Optional["ApiKey"] = Relationship(back_populates="user")
    def __repr__(self):
        return f"<User {self.email}>"


class Author(SQLModel, table=True):
    __tablename__ = "authors"

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str

    # Relationships
    books: List["Book"] = Relationship(back_populates="authors", sa_relationship_kwargs={"lazy": "selectin"})


class Publisher(SQLModel, table=True):
    __tablename__ = "publishers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None

    # Relationships
    books: List["Book"] = Relationship(back_populates="publisher", sa_relationship_kwargs={"lazy": "selectin"})


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    category_name: str = Field(unique=True, index=True)
    description: Optional[str] = None

    books: List["Book"] = Relationship(back_populates="categories", sa_relationship_kwargs={"lazy": "selectin"})


class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: Optional[int] = Field(default=None, primary_key=True)
    isbn: str = Field(unique=True, index=True)
    title: str = Field(index=True)
    author_id: Optional[int] = Field(default=None, foreign_key="authors.id")
    publisher_id: Optional[int] = Field(default=None, foreign_key="publishers.id")
    publication_date: Optional[date] = None
    edition: Optional[str] = None
    language: str = "English"
    category: Optional[int] = Field(default=None, foreign_key="categories.id")
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP, nullable=False))
    updated_at: datetime = Field(default_factory=datetime.now,
                                 sa_column=Column(pg.TIMESTAMP, nullable=False, onupdate=datetime.now))

    # Relationships
    publisher: Optional[Publisher] = Relationship(back_populates="books", sa_relationship_kwargs={"lazy": "selectin"})
    categories: List[Category] = Relationship(back_populates="books", sa_relationship_kwargs={"lazy": "selectin"})
    authors: List[Author] = Relationship(back_populates="books", sa_relationship_kwargs={"lazy": "selectin"})
    book_copies: List["BookCopy"] = Relationship(back_populates="book", sa_relationship_kwargs={"lazy": "selectin"})


class BookCopy(SQLModel, table=True):
    __tablename__ = "book_copies"

    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id", index=True)
    copy_number: str = Field(unique=True, index=True)
    price: Optional[float] = None
    status: BoookCopyStatus = Field(default=BoookCopyStatus.AVAILABLE, sa_column=Column(pg.VARCHAR(20)))
    location: Optional[str] = None
    condition: Optional[str] = None
    notes: Optional[str] = None

    # Relationships
    book: Book = Relationship(back_populates="book_copies")
    borrowings: List["Borrowing"] = Relationship(back_populates="book_copy", sa_relationship_kwargs={"lazy": "selectin"})


class Borrowing(SQLModel, table=True):
    __tablename__ = "borrowings"

    id: Optional[int] = Field(default=None, primary_key=True)
    copy_id: int = Field(foreign_key="book_copies.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    borrowed_date: datetime = Field(default_factory=datetime.now)
    due_date: datetime
    returned_date: Optional[datetime] = None
    extended_times: int = 0
    status: BorrowingStatus = Field(default=BorrowingStatus.REQUESTED)
    notes: Optional[str] = None
    accepted_by: int = Field(nullable=True, foreign_key="users.id")  # Librarian ID

    # Relationships
    lended_user: Optional[User] =Relationship(sa_relationship_kwargs={"foreign_keys": "[Borrowing.accepted_by]"})
    user: Optional[User] = Relationship(back_populates="borrowings", sa_relationship_kwargs={"foreign_keys": "[Borrowing.user_id]"})
    book_copy: BookCopy = Relationship(back_populates="borrowings")


class ApiKey(SQLModel, table=True):
    __tablename__ = "api_keys"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(index=True)  # This will store the encrypted API key (in base64)
    hashed_key: str = Field(index=True)  # This will store hashed API key for lookup
    created_at: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="users.id")  # Foreign key to the user who owns this key

    user: "User" = Relationship(back_populates="api_keys")
