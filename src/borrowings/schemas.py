from datetime import datetime, date
from typing import Optional

from sqlmodel import SQLModel

from src.filters import FilterParams
from src.db.enums import BorrowingStatus
from src.books.schemas import BookCopyModel


class BorrowingModel(SQLModel):
    id: int
    copy_id: int
    user_id: int
    borrowed_date: datetime
    due_date: datetime
    returned_date: Optional[datetime]
    extended_times: int = 0
    status: BorrowingStatus
    notes: Optional[str]


class BorrowingCreateModel(SQLModel):
    copy_id: int
    user_id: Optional[int] = 0
    due_date: date
    status: BorrowingStatus = BorrowingStatus.REQUESTED
    notes: Optional[str]


class UserBorrowingModel(SQLModel):
    email: str
    first_name: str
    last_name: str
    role: str


class BorrowingUpdateModel(SQLModel):
    returned_date: Optional[datetime]
    due_date: Optional[datetime]
    extended_times: Optional[int]
    status: Optional[BorrowingStatus]
    notes: Optional[str]


class BorrowingHistoryModel(SQLModel):
    id: int
    borrowing_id: int
    status: BorrowingStatus
    changed_at: datetime
    notes: Optional[str]


class BorrowResponseModel(BorrowingModel):
    user: UserBorrowingModel
    lended_user: Optional[UserBorrowingModel]
    book_copy: Optional[BookCopyModel]


class BorrowingFilterParams(FilterParams):
    copy_id: Optional[int] = None
    borrowed_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    returned_date: Optional[datetime] = None
    status: Optional[BorrowingStatus] = None
    accepted_by: Optional[int] = None