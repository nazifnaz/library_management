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

