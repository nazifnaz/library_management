# Borrow request, update, withdraw by user

from typing import List, Annotated

# Borrow accept, manage by librarian
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from . import schemas
from .services import BorrowService
from ..auth.dependencies import get_current_user, RoleChecker
from ..db.enums import UserRole
from ..db.models import User

router = APIRouter()

borrow_service = BorrowService()
admin_or_librarian_role_checker = RoleChecker([UserRole.ADMIN, UserRole.LIBRARIAN])


# Borrowing routes
@router.post("/", response_model=schemas.BorrowingModel)
async def create_borrowing(borrowing: schemas.BorrowingCreateModel, session: AsyncSession = Depends(get_session),
                           current_user: User = Depends(get_current_user)):
    borrowing.user_id = current_user.id
    borrow = await borrow_service.create_borrowing(session, borrowing)
    return borrow


@router.get("/{borrowing_id}", response_model=schemas.BorrowResponseModel)
async def read_borrowing(borrowing_id: int, session: AsyncSession = Depends(get_session),
                         current_user: User = Depends(get_current_user)):
    borrowing = await borrow_service.get_borrowing(session, borrowing_id, user=current_user)
    if not borrowing:
        raise HTTPException(status_code=404, detail="Borrowing not found")
    return borrowing


@router.get("/", response_model=List[schemas.BorrowResponseModel])
async def read_borrowings(
        filter_params: Annotated[schemas.BorrowingFilterParams, Query()],
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    filters = filter_params.model_dump()
    return await borrow_service.get_borrowings(session, user=current_user, **filters)


@router.put("/{borrowing_id}", response_model=schemas.BorrowResponseModel)
async def update_borrowing(borrowing_id: int, borrowing: schemas.BorrowingUpdateModel,
                           session: AsyncSession = Depends(get_session),
                           current_user: User = Depends(get_current_user)):
    updated_borrowing = await borrow_service.update_borrowing(session, borrowing_id, borrowing, user=current_user)
    if not updated_borrowing:
        raise HTTPException(status_code=404, detail="Borrowing not found")
    return updated_borrowing


@router.delete("/{borrowing_id}", response_model=schemas.BorrowResponseModel)
async def delete_borrowing(borrowing_id: int, session: AsyncSession = Depends(get_session),
                           _: bool = Depends(admin_or_librarian_role_checker)):
    deleted = await borrow_service.delete_borrowing(session, borrowing_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Borrowing not found")
    return {"detail": "Borrowing deleted successfully"}
