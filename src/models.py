import datetime
from typing import Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpenseCreate(BaseModel):
    """
    Schema for creating a new expense.
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Title or description of the expense",
        json_schema_extra={"example": "Grocery Shopping"}
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Amount of the expense in positive numeric value",
        json_schema_extra={"example": 45.99}
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Category of the expense (e.g., Food, Travel, Utilities)",
        json_schema_extra={"example": "Food"}
    )
    date: datetime.date = Field(
        ...,
        description="Date of the expense in ISO-8601 format (YYYY-MM-DD)",
        json_schema_extra={"example": "2026-07-31"}
    )

    @field_validator("title", "category", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("String field cannot be empty or blank whitespace")
        return value

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "title": "Team Lunch",
                "amount": 35.50,
                "category": "Food",
                "date": "2026-07-31",
            }
        },
    )


class Expense(ExpenseCreate):
    """
    Schema representing a stored expense including its unique ID.
    """
    id: str = Field(
        ...,
        description="Unique UUIDv4 identifier for the expense",
        json_schema_extra={"example": "c303282d-f2e6-46ca-a04a-35d3d873712d"}
    )


class TotalResponse(BaseModel):
    """
    Schema for expense totals calculation response.
    """
    total: float = Field(
        ...,
        description="Total sum of all expenses",
        json_schema_extra={"example": 150.75}
    )
    by_category: Dict[str, float] = Field(
        ...,
        description="Total sum of expenses grouped by category",
        json_schema_extra={"example": {"Food": 45.99, "Travel": 104.76}}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 150.75,
                "by_category": {
                    "Food": 45.99,
                    "Travel": 104.76
                }
            }
        }
    )
