from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel

from src.db.enums import BookCopyStatus


class AuthorModel(SQLModel):
    id: int
    first_name: str
    last_name: str


class AuthorCreateModel(SQLModel):
    first_name: str
    last_name: str


class AuthorUpdateModel(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class PublisherModel(SQLModel):
    id: int
    name: str
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None


class PublisherCreateModel(SQLModel):
    name: str
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None


class PublisherUpdateModel(SQLModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None


class CategoryModel(SQLModel):
    id: int
    category_name: str
    description: Optional[str] = None


class CategoryCreateModel(SQLModel):
    category_name: str
    description: Optional[str] = None


class CategoryUpdateModel(SQLModel):
    category_name: Optional[str] = None
    description: Optional[str] = None


class BookModel(SQLModel):
    id: int
    isbn: str
    title: str
    publisher_id: int
    publication_date: datetime
    edition: str
    language: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


class BookCreateModel(SQLModel):
    isbn: str
    title: str
    authors: List[int]
    publisher_id: int
    publication_date: datetime
    edition: str
    language: str
    categories: List[int]
    description: Optional[str]


class BookUpdateModel(SQLModel):
    isbn: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[List[int]] = None
    publisher_id: Optional[int] = None
    publication_date: Optional[datetime] = None
    edition: Optional[str] = None
    language: Optional[str] = None
    categories: Optional[List[int]] = None
    description: Optional[str] = None


class BookCopyModel(SQLModel):
    id: int
    book_id: int
    copy_number: str
    price: Optional[float]
    status: BookCopyStatus
    location: Optional[str]
    condition: Optional[str]
    notes: Optional[str]


class BookCopyCreateModel(SQLModel):
    book_id: int
    copy_number: str
    price: Optional[float] = None
    status: BookCopyStatus
    location: Optional[str] = None
    condition: Optional[str] = None
    notes: Optional[str] = None


class BookCopyUpdateModel(SQLModel):
    book_id: Optional[int] = None
    copy_number: Optional[str] = None
    price: Optional[float] = None
    status: Optional[BookCopyStatus] = None
    location: Optional[str] = None
    condition: Optional[str] = None
    notes: Optional[str] = None


class BookCopyResponseModel(SQLModel):
    book_id: int
    copy_number: str
    price: Optional[float] = None
    status: BookCopyStatus
    location: Optional[str] = None
    condition: Optional[str] = None
    notes: Optional[str] = None


class AuthorResponseModel(AuthorModel):
    books: List[BookModel]


class PublisherResponseModel(PublisherModel):
    books: List[BookModel]


class CategoryResponseModel(CategoryModel):
    books: List[BookModel]


class BookResponseModel(BookModel):
    authors: List[AuthorModel]
    publisher: PublisherModel
    categories: List[CategoryModel]
    book_copies: List[BookCopyModel]
