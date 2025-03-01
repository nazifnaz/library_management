from enum import Enum


class UserRole(str, Enum):
    """
    Enum for user roles.
    """
    ADMIN = "admin"
    USER = "user"


class BoookCopyStatus(str, Enum):
    """
    Enum for bookcopy status.
    """
    AVAILABLE = "available"
    BORROWED = "borrowed"


class BorrowingStatus(str, Enum):
    """
    Enum for borrowing status.
    """
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"
    LOST = "lost"


