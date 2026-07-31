import threading
import uuid
from typing import Dict, List, Optional
from src.models import Expense, ExpenseCreate, TotalResponse


class ExpenseRepository:
    """
    Thread-safe in-memory storage repository for managing personal expenses.
    """
    def __init__(self) -> None:
        self._store: Dict[str, Expense] = {}
        self._lock = threading.RLock()

    def add_expense(self, expense_in: ExpenseCreate) -> Expense:
        with self._lock:
            expense_id = str(uuid.uuid4())
            expense = Expense(
                id=expense_id,
                title=expense_in.title,
                amount=expense_in.amount,
                category=expense_in.category,
                date=expense_in.date
            )
            self._store[expense_id] = expense
            return expense

    def get_all(self, category: Optional[str] = None) -> List[Expense]:
        with self._lock:
            expenses = list(self._store.values())
            if category and category.strip():
                target_cat = category.strip().lower()
                expenses = [
                    e for e in expenses
                    if e.category.strip().lower() == target_cat
                ]
            return expenses

    def get_by_id(self, expense_id: str) -> Optional[Expense]:
        with self._lock:
            return self._store.get(expense_id)

    def delete_expense(self, expense_id: str) -> bool:
        with self._lock:
            if expense_id in self._store:
                del self._store[expense_id]
                return True
            return False

    def get_totals(self) -> TotalResponse:
        with self._lock:
            total_amount = round(sum(item.amount for item in self._store.values()), 2)
            
            # Group by category case-insensitively while preserving clear category casing
            by_category_map: Dict[str, float] = {}
            # Track display name for each lowercased category key
            display_names: Dict[str, str] = {}

            for item in self._store.values():
                lower_cat = item.category.strip().lower()
                if lower_cat not in display_names:
                    display_names[lower_cat] = item.category.strip()
                by_category_map[lower_cat] = by_category_map.get(lower_cat, 0.0) + item.amount

            # Build final by_category dict with rounded amounts
            by_category: Dict[str, float] = {
                display_names[lower_cat]: round(amount, 2)
                for lower_cat, amount in by_category_map.items()
            }

            return TotalResponse(
                total=total_amount,
                by_category=by_category
            )

    def clear(self) -> None:
        """
        Clear all stored expenses. Essential for automated test isolation.
        """
        with self._lock:
            self._store.clear()


# Singleton repository instance for application routes
repository = ExpenseRepository()
