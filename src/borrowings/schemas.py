from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel

from src.db.enums import BorrowingStatus


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
    user_id: int
    borrowed_date: datetime
    due_date: datetime
    notes: Optional[str]


class BorrowingUpdateModel(SQLModel):
    returned_date: Optional[datetime]
    extended_times: Optional[int]
    status: Optional[BorrowingStatus]
    notes: Optional[str]


class BorrowingHistoryModel(SQLModel):
    id: int
    borrowing_id: int
    status: BorrowingStatus
    changed_at: datetime
    notes: Optional[str]
