from typing import List, Annotated

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from . import schemas
from .services import (
    BookService,
    AuthorService,
    PublisherService,
    CategoryService,
    BookCopyService,
)
from ..auth.dependencies import RoleChecker
from ..db.enums import UserRole

book_router = APIRouter()

# Book routes

book_service = BookService()
admin_or_librarian_role_checker = RoleChecker([UserRole.ADMIN, UserRole.LIBRARIAN])


@book_router.post("/books/", response_model=schemas.BookResponseModel)
async def create_book(book: schemas.BookCreateModel, session: AsyncSession = Depends(get_session),
                      _: bool = Depends(admin_or_librarian_role_checker)):
    return await book_service.create_book(book, session)


@book_router.get("/books/{book_id}", response_model=schemas.BookResponseModel)
async def get_book(book_id: int, session: AsyncSession = Depends(get_session)):
    book = await book_service.get_book_by_id(book_id, session)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@book_router.get("/books/", response_model=List[schemas.BookResponseModel])
async def get_books(filter_params: Annotated[schemas.BookFilterParams, Query()], session: AsyncSession = Depends(get_session)):
    params = filter_params.model_dump()
    return await book_service.get_books(session, **params)


@book_router.put("/books/{book_id}", response_model=schemas.BookResponseModel)
async def update_book(book_id: int, book: schemas.BookUpdateModel, session: AsyncSession = Depends(get_session),
                      _: bool = Depends(admin_or_librarian_role_checker)):
    updated_book = await book_service.update_book(book_id, book, session)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book


@book_router.delete("/books/{book_id}", response_model=schemas.BookResponseModel)
async def delete_book(book_id: int, session: AsyncSession = Depends(get_session),
                      _: bool = Depends(admin_or_librarian_role_checker)):
    deleted_book = await BookService().delete_book(book_id, session)
    if not deleted_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return deleted_book


# Author routes

author_service = AuthorService()


@book_router.post("/authors/", response_model=schemas.AuthorResponseModel)
async def create_author(author: schemas.AuthorCreateModel, session: AsyncSession = Depends(get_session),
                        _: bool = Depends(admin_or_librarian_role_checker)):
    return await author_service.create_author(author, session)


@book_router.get("/authors/{author_id}", response_model=schemas.AuthorResponseModel)
async def get_author(author_id: int, session: AsyncSession = Depends(get_session)):
    author = await author_service.get_author_by_id(author_id, session)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@book_router.get("/authors/", response_model=List[schemas.AuthorResponseModel])
async def get_authors(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    return await author_service.get_authors(session, skip, limit)


@book_router.put("/authors/{author_id}", response_model=schemas.AuthorResponseModel)
async def update_author(author_id: int, author: schemas.AuthorUpdateModel,
                        session: AsyncSession = Depends(get_session),
                        _: bool = Depends(admin_or_librarian_role_checker)):
    updated_author = await author_service.update_author(author_id, author, session)
    if not updated_author:
        raise HTTPException(status_code=404, detail="Author not found")
    return updated_author


@book_router.delete("/authors/{author_id}", response_model=schemas.AuthorResponseModel)
async def delete_author(author_id: int, session: AsyncSession = Depends(get_session),
                        _: bool = Depends(admin_or_librarian_role_checker)):
    deleted_author = await author_service.delete_author(author_id, session)
    if not deleted_author:
        raise HTTPException(status_code=404, detail="Author not found")
    return deleted_author


# Publisher routes

publisher_service = PublisherService()


@book_router.post("/publishers/", response_model=schemas.PublisherResponseModel)
async def create_publisher(publisher: schemas.PublisherCreateModel, session: AsyncSession = Depends(get_session),
                           _: bool = Depends(admin_or_librarian_role_checker)):
    return await publisher_service.create_publisher(publisher, session)


@book_router.get("/publishers/{publisher_id}", response_model=schemas.PublisherResponseModel)
async def get_publisher(publisher_id: int, session: AsyncSession = Depends(get_session)):
    publisher = await publisher_service.get_publisher_by_id(publisher_id, session)
    if not publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return publisher


@book_router.get("/publishers/", response_model=List[schemas.PublisherResponseModel])
async def get_publishers(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    return await publisher_service.get_publishers(session, skip, limit)


@book_router.put("/publishers/{publisher_id}", response_model=schemas.PublisherResponseModel)
async def update_publisher(publisher_id: int, publisher: schemas.PublisherUpdateModel,
                           session: AsyncSession = Depends(get_session),
                           _: bool = Depends(admin_or_librarian_role_checker)):
    updated_publisher = await publisher_service.update_publisher(publisher_id, publisher, session)
    if not updated_publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return updated_publisher


@book_router.delete("/publishers/{publisher_id}", response_model=schemas.PublisherResponseModel)
async def delete_publisher(publisher_id: int, session: AsyncSession = Depends(get_session),
                           _: bool = Depends(admin_or_librarian_role_checker)):
    deleted_publisher = await publisher_service.delete_publisher(publisher_id, session)
    if not deleted_publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return deleted_publisher


# Category routes

category_service = CategoryService()


@book_router.post("/categories/", response_model=schemas.CategoryResponseModel)
async def create_category(category: schemas.CategoryCreateModel, session: AsyncSession = Depends(get_session),
                          _: bool = Depends(admin_or_librarian_role_checker)):
    return await category_service.create_category(category, session)


@book_router.get("/categories/{category_id}", response_model=schemas.CategoryResponseModel)
async def get_category(category_id: int, session: AsyncSession = Depends(get_session)):
    category = await category_service.get_category_by_id(category_id, session)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@book_router.get("/categories/", response_model=List[schemas.CategoryResponseModel])
async def get_categories(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    return await category_service.get_categories(session, skip, limit)


@book_router.put("/categories/{category_id}", response_model=schemas.CategoryResponseModel)
async def update_category(category_id: int, category: schemas.CategoryUpdateModel,
                          session: AsyncSession = Depends(get_session),
                          _: bool = Depends(admin_or_librarian_role_checker)):
    updated_category = await category_service.update_category(category_id, category, session)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category


@book_router.delete("/categories/{category_id}", response_model=schemas.CategoryResponseModel)
async def delete_category(category_id: int, session: AsyncSession = Depends(get_session)):
    deleted_category = await category_service.delete_category(category_id, session)
    if not deleted_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return deleted_category


# BookCopy routes

book_copy_service = BookCopyService()


@book_router.post("/book_copies/", response_model=schemas.BookCopyResponseModel)
async def create_book_copy(book_copy: schemas.BookCopyCreateModel, session: AsyncSession = Depends(get_session)):
    return await book_copy_service.create_book_copy(book_copy, session)


@book_router.get("/book_copies/{book_copy_id}", response_model=schemas.BookCopyResponseModel)
async def get_book_copy(book_copy_id: int, session: AsyncSession = Depends(get_session)):
    book_copy = await book_copy_service.get_book_copy_by_id(book_copy_id, session)
    if not book_copy:
        raise HTTPException(status_code=404, detail="Book copy not found")
    return book_copy


@book_router.get("/book_copies/", response_model=List[schemas.BookCopyResponseModel])
async def get_book_copies(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)):
    return await book_copy_service.get_book_copies(session, skip, limit)


@book_router.put("/book_copies/{book_copy_id}", response_model=schemas.BookCopyResponseModel)
async def update_book_copy(book_copy_id: int, book_copy: schemas.BookCopyUpdateModel,
                           session: AsyncSession = Depends(get_session)):
    updated_book_copy = await book_copy_service.update_book_copy(book_copy_id, book_copy, session)
    if not updated_book_copy:
        raise HTTPException(status_code=404, detail="Book copy not found")
    return updated_book_copy


@book_router.delete("/book_copies/{book_copy_id}", response_model=schemas.BookCopyResponseModel)
async def delete_book_copy(book_copy_id: int, session: AsyncSession = Depends(get_session),
                           _: bool = Depends(admin_or_librarian_role_checker)):
    deleted_book_copy = await book_copy_service.delete_book_copy(book_copy_id, session)
    if not deleted_book_copy:
        raise HTTPException(status_code=404, detail="Book copy not found")
    return deleted_book_copy
