from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from src.models import Expense, ExpenseCreate, TotalResponse
from src.repository import repository

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post(
    "",
    response_model=Expense,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new expense",
    description="Creates a new personal expense with an auto-generated UUIDv4."
)
def create_expense(expense_in: ExpenseCreate) -> Expense:
    return repository.add_expense(expense_in)


@router.get(
    "",
    response_model=List[Expense],
    status_code=status.HTTP_200_OK,
    summary="View all expenses or filter by category",
    description="Returns a list of expenses. Can be optionally filtered by category."
)
def get_expenses(
    category: Optional[str] = Query(
        default=None,
        description="Filter expenses by case-insensitive category name"
    )
) -> List[Expense]:
    return repository.get_all(category=category)


@router.get(
    "/total",
    response_model=TotalResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate total expenses",
    description="Returns the overall total expense amount and totals grouped by category."
)
def get_totals() -> TotalResponse:
    return repository.get_totals()


@router.get(
    "/{expense_id}",
    response_model=Expense,
    status_code=status.HTTP_200_OK,
    summary="Get an expense by ID",
    description="Retrieves a single expense by its unique UUIDv4."
)
def get_expense_by_id(expense_id: str) -> Expense:
    expense = repository.get_by_id(expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID '{expense_id}' was not found"
        )
    return expense


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense",
    description="Deletes an expense by its unique UUIDv4. Returns 404 if the ID does not exist."
)
def delete_expense(expense_id: str) -> None:
    deleted = repository.delete_expense(expense_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID '{expense_id}' was not found"
        )
