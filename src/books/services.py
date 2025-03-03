from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import (
    Author,
    Publisher,
    Category,
    Book,
    BookCopy,
    BookAuthor,
    BookCategory,
)
from .schemas import (
    BookCreateModel,
    BookUpdateModel,
    AuthorCreateModel,
    AuthorUpdateModel,
    PublisherCreateModel,
    PublisherUpdateModel,
    CategoryCreateModel,
    CategoryUpdateModel,
    BookCopyCreateModel,
    BookCopyUpdateModel,
)


class BookService:
    async def get_book_by_id(self, book_id: int, session: AsyncSession):
        book = await session.exec(select(Book).where(Book.id == book_id))
        return book.first()

    async def get_book_by_isbn(self, isbn: str, session: AsyncSession):
        book = await session.exec(select(Book).where(Book.isbn == isbn))
        return book.first()

    async def get_book_by_title(self, title: str, session: AsyncSession):
        book = await session.exec(select(Book).where(Book.title == title))
        return book.first()

    async def get_books(self, session: AsyncSession, publisher_id: Optional[int] = None,
                        title: Optional[str] = None, offset: int = 0, limit: int = 10):
        statement = select(Book)
        if publisher_id:
            statement = statement.where(Book.publisher_id == publisher_id)
        if title:
            statement = statement.where(Book.title == title)

        statement = statement.offset(offset).limit(limit)
        books = await session.exec(statement)
        return books.all()

    async def get_books_by_publisher(self, publisher_id: int, session: AsyncSession, skip: int = 0, limit: int = 10):
        books = await session.exec(select(Book).where(Book.publisher_id == publisher_id).offset(skip).limit(limit))
        return books.all()

    async def get_books_by_category(self, category_id: int, session: AsyncSession, skip: int = 0, limit: int = 10):
        books = await session.exec(
            select(Book)
                .join(BookCategory)
                .where(BookCategory.category_id == category_id)
                .offset(skip)
                .limit(limit)
        )

        return books.all()

    async def get_books_by_author(self, author_id: int, session: AsyncSession, skip: int = 0, limit: int = 10):
        books = await session.exec(
            select(Book)
                .join(BookAuthor)
                .where(BookAuthor.author_id == author_id)
                .offset(skip)
                .limit(limit)
        )

        return books.all()

    async def create_book(self, book: BookCreateModel, session: AsyncSession):
        db_book = await self.get_book_by_isbn(book.isbn, session)
        if db_book:
            raise ValueError("Book with this ISBN already exists")
        book_data_dict = book.model_dump()
        authors = book_data_dict.pop("authors", None)
        categories = book_data_dict.pop("categories", None)
        publisher_id = book_data_dict.get("publisher_id")
        if publisher_id is not None:
            publisher = await PublisherService().get_publisher_by_id(publisher_id, session)
            if publisher is None:
                raise ValueError(f"Publisher with ID {publisher_id} not found")

        new_book = Book(**book_data_dict)
        session.add(new_book)
        await session.flush()

        # Process authors
        await self._add_authors_to_book(new_book, authors, session)

        # Process categories
        await self._add_categories_to_book(new_book, categories, session)

        await session.commit()
        await session.refresh(new_book)
        return new_book

    async def _add_authors_to_book(self, book: Book, author_ids: List[int], session: AsyncSession) -> None:
        """Add authors to the book based on the provided IDs."""
        # Validate all authors exist
        for author_id in author_ids:
            result = await session.exec(select(Author).where(Author.id == author_id))

            author = result.first()
            if not author:
                await session.rollback()
                raise ValueError(f"Author with ID {author_id} not found")

            # Create the link
            book_author_link = BookAuthor(book_id=book.id, author_id=author_id)
            session.add(book_author_link)

    async def _add_categories_to_book(self, book: Book, category_ids: List[int], session: AsyncSession) -> None:
        """Add categories to the book based on the provided IDs."""
        # Validate all categories exist
        for category_id in category_ids:
            result = await session.exec(select(Category).where(Category.id == category_id))
            category = result.first()
            if not category:
                await session.rollback()
                raise ValueError(f"Category with ID {category_id} not found")

            # Create the link
            book_category_link = BookCategory(book_id=book.id, category_id=category_id)
            session.add(book_category_link)

    async def update_book(self, book_id: int, book: BookUpdateModel, session: AsyncSession):
        db_book: Book = await self.get_book_by_id(book_id, session)
        if not db_book:
            raise ValueError("Book not found")
        book_data = book.model_dump(exclude_unset=True)
        authors = book_data.pop("authors", None)
        categories = book_data.pop("categories", None)
        publisher_id = book_data.get("publisher_id")
        if publisher_id is not None:
            publisher = await PublisherService().get_publisher_by_id(publisher_id, session)
            if publisher is None:
                raise ValueError(f"Publisher with ID {publisher_id} not found")

        for key, value in book_data.items():
            setattr(db_book, key, value)

        from sqlalchemy import delete

        # Clear existing relationships
        await session.exec(delete(BookAuthor).where(BookAuthor.book_id == book_id))
        await session.exec(delete(BookCategory).where(BookCategory.book_id == book_id))
        if authors:
            # Add new relationships
            await self._add_authors_to_book(db_book, authors, session)
        if categories:
            await self._add_categories_to_book(db_book, categories, session)

        await session.commit()
        await session.refresh(db_book)
        return db_book

    async def delete_book(self, book_id: int, session: AsyncSession):
        db_book = await self.get_book_by_id(book_id, session)
        if not db_book:
            raise ValueError("Book not found")

        await session.delete(db_book)
        await session.commit()
        return db_book


class AuthorService:

    async def get_author_by_id(self, author_id: int, session: AsyncSession):
        author = await session.exec(select(Author).where(Author.id == author_id))
        return author.first()

    async def get_authors(self, session: AsyncSession, skip: int = 0, limit: int = 10):
        authors = await session.exec(select(Author).offset(skip).limit(limit))
        return authors.all()

    async def create_author(self, author: AuthorCreateModel, session: AsyncSession):
        new_author = Author(**author.model_dump())
        session.add(new_author)
        await session.commit()
        await session.refresh(new_author)
        return new_author

    async def update_author(self, author_id: int, author: AuthorUpdateModel, session: AsyncSession):
        db_author = await self.get_author_by_id(author_id, session)
        if not db_author:
            raise ValueError("Author not found")

        for key, value in author.model_dump(exclude_unset=True).items():
            setattr(db_author, key, value)

        session.add(db_author)
        await session.commit()
        await session.refresh(db_author)
        return db_author

    async def delete_author(self, author_id: int, session: AsyncSession):
        db_author = await self.get_author_by_id(author_id, session)
        if not db_author:
            return None
        await session.delete(db_author)
        await session.commit()
        return db_author


class PublisherService:
    async def get_publisher_by_id(self, publisher_id: int, session: AsyncSession):
        publisher = await session.exec(select(Publisher).where(Publisher.id == publisher_id))
        return publisher.first()

    async def get_publishers(self, session: AsyncSession, skip: int = 0, limit: int = 10):
        publishers = await session.exec(select(Publisher).offset(skip).limit(limit))
        return publishers.all()

    async def create_publisher(self, publisher: PublisherCreateModel, session: AsyncSession):
        new_publisher = Publisher(**publisher.model_dump())
        session.add(new_publisher)
        await session.commit()
        await session.refresh(new_publisher)
        return new_publisher

    async def update_publisher(self, publisher_id: int, publisher: PublisherUpdateModel, session: AsyncSession):
        db_publisher = await self.get_publisher_by_id(publisher_id, session)
        if not db_publisher:
            return None
        for key, value in publisher.model_dump(exclude_unset=True).items():
            setattr(db_publisher, key, value)
        session.add(db_publisher)
        await session.commit()
        await session.refresh(db_publisher)
        return db_publisher

    async def delete_publisher(self, publisher_id: int, session: AsyncSession):
        db_publisher = await self.get_publisher_by_id(publisher_id, session)
        if not db_publisher:
            return None
        await session.delete(db_publisher)
        await session.commit()
        return db_publisher


class CategoryService:
    async def get_category_by_id(self, category_id: int, session: AsyncSession):
        category = await session.exec(select(Category).where(Category.id == category_id))
        return category.first()

    async def get_category_by_name(self, category_name: str, session: AsyncSession):
        category = await session.exec(select(Category).where(Category.category_name == category_name))
        return category.first()

    async def get_categories(self, session: AsyncSession, skip: int = 0, limit: int = 10):
        categories = await session.exec(select(Category).offset(skip).limit(limit))
        return categories.all()

    async def create_category(self, category: CategoryCreateModel, session: AsyncSession):
        db_category = await self.get_category_by_name(category.category_name, session)
        if db_category:
            raise ValueError("Category with this name already exists")

        new_category = Category(**category.model_dump())
        session.add(new_category)
        await session.commit()
        await session.refresh(new_category)
        return new_category

    async def update_category(self, category_id: int, category: CategoryUpdateModel, session: AsyncSession):
        db_category = await self.get_category_by_id(category_id, session)
        if not db_category:
            raise ValueError("Category not found")

        for key, value in category.model_dump(exclude_unset=True).items():
            setattr(db_category, key, value)
        session.add(db_category)
        await session.commit()
        await session.refresh(db_category)
        return db_category

    async def delete_category(self, category_id: int, session: AsyncSession):
        db_category = await self.get_category_by_id(category_id, session)
        if not db_category:
            return None
        await session.delete(db_category)
        await session.commit()
        return db_category


class BookCopyService:
    async def get_book_copy_by_id(self, book_copy_id: int, session: AsyncSession):
        book_copy = await session.exec(select(BookCopy).where(BookCopy.id == book_copy_id))
        return book_copy.first()

    async def get_book_copy_by_copy_number(self, copy_number: str, session: AsyncSession):
        book_copy = await session.exec(select(BookCopy).where(BookCopy.copy_number == copy_number))
        return book_copy.first()

    async def get_book_copies(self, session: AsyncSession, skip: int = 0, limit: int = 10):
        book_copies = await session.exec(select(BookCopy).offset(skip).limit(limit))
        return book_copies.all()

    async def create_book_copy(self, book_copy: BookCopyCreateModel, session: AsyncSession):
        book_id = book_copy.get("book_id")
        book = await BookService().get_book_by_id(book_id, session)
        if book is None:
            raise ValueError(f"Book with id {book_id} does not exist.")
        new_book_copy = BookCopy(**book_copy.model_dump())
        session.add(new_book_copy)
        await session.commit()
        await session.refresh(new_book_copy)
        return new_book_copy

    async def update_book_copy(self, book_copy_id: int, book_copy: BookCopyUpdateModel, session: AsyncSession):
        book_copy = book_copy.model_dump(exclude_unset=True)
        book_id = book_copy.get("book_id")
        book = await BookService().get_book_by_id(book_id, session)
        if book is None:
            raise ValueError(f"Book with id {book_id} does not exist.")
        db_book_copy = await self.get_book_copy_by_id(book_copy_id, session)
        if not db_book_copy:
            raise ValueError("Book copy not found")

        for key, value in book_copy.items():
            setattr(db_book_copy, key, value)

        session.add(db_book_copy)
        await session.commit()
        await session.refresh(db_book_copy)
        return db_book_copy

    async def delete_book_copy(self, book_copy_id: int, session: AsyncSession):
        db_book_copy = await self.get_book_copy_by_id(book_copy_id, session)
        if not db_book_copy:
            raise ValueError("Book copy not found")

        await session.delete(db_book_copy)
        await session.commit()
        return db_book_copy
