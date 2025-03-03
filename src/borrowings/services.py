from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.enums import BorrowingStatus
from src.db.models import Borrowing, User
from .schemas import BorrowingCreateModel, BorrowingUpdateModel
from ..errors import InsufficientPermission


class BorrowService:
    async def create_borrowing(self, session: AsyncSession, borrowing_data: BorrowingCreateModel):
        borrowing = borrowing_data.model_dump()
        borrowing = Borrowing(**borrowing)
        session.add(borrowing)
        await session.commit()
        await session.refresh(borrowing)
        return borrowing

    async def get_borrowing(self, session: AsyncSession, borrowing_id: int, user: User):
        statement = select(Borrowing).where(Borrowing.id == borrowing_id)
        result = await session.exec(statement)
        borrowing = result.first()
        if borrowing is None:
            return None
        return borrowing

    async def get_borrowings(
            self,
            session: AsyncSession,
            skip: int = 0,
            limit: int = 10,
            copy_id: Optional[int] = None,
            status: Optional[BorrowingStatus] = None,
            accepted_by: Optional[int] = None,
            user: User=None,
    ):
        statement = select(Borrowing)

        if not user.is_librarian():
            statement = statement.where(Borrowing.user_id == user.id)
        if copy_id is not None:
            statement = statement.where(Borrowing.copy_id == copy_id)
        if status is not None:
            statement = statement.where(Borrowing.status == status)
        if accepted_by is not None:
            statement = statement.where(Borrowing.accepted_by == accepted_by)

        statement = statement.offset(skip).limit(limit)
        result = await session.exec(statement)
        borrowings = result.all()
        return borrowings

    async def update_borrowing(self, session: AsyncSession, borrowing_id: int, borrowing_data: BorrowingUpdateModel, user: User):
        statement = select(Borrowing).where(Borrowing.id == borrowing_id)
        result = await session.exec(statement)
        borrowing = result.first()
        if borrowing is None:
            return None
        if not user.is_librarian() and borrowing.user_id != user.id:
            raise InsufficientPermission()

        for key, value in borrowing_data.model_dump(exclude_unset=True).items():
            setattr(borrowing, key, value)
        session.add(borrowing)
        await session.commit()
        await session.refresh(borrowing)
        return borrowing

    async def delete_borrowing(self, session: AsyncSession, borrowing_id: int) -> bool:
        statement = select(Borrowing).where(Borrowing.id == borrowing_id)
        result = await session.exec(statement)
        borrowing = result.first()
        if borrowing is None:
            return False
        await session.delete(borrowing)
        await session.commit()
        return True
