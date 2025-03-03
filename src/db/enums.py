from enum import Enum


class UserRole(str, Enum):
    """
    Enum for user roles.
    """
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    USER = "user"


class BookCopyStatus(str, Enum):
    """
    Enum for bookcopy status.
    """
    AVAILABLE = "available"
    BORROWED = "borrowed"


class BorrowingStatus(str, Enum):
    """
    Enum for borrowing status.
    """
    REQUESTED = "requested"
    ACTIVE = "active"
    RETURN_REQUESTED = "return_requested"
    RETURNED = "returned"
    OVERDUE = "overdue"
    LOST = "lost"


