# Smart Expense Tracker API

A production-ready RESTful API to manage personal expenses, built with Python 3, FastAPI, and Pydantic for the Diligent Corporation Software Engineering Apprenticeship 2026 assignment.

---

## Key Features and Bonus Implemented

- Full CRUD Support: Add, view, delete, and inspect personal expenses.
- Case-Insensitive Category Filtering: Seamlessly filter expenses by category (/expenses?category=Food).
- Precision Totals Calculation: Calculate overall total expenses and breakdown by category with floating-point precision rounding (/expenses/total).
- Robust Edge Case and Input Validation: Validates positive amounts (> 0), non-empty strings, strict ISO-8601 dates (YYYY-MM-DD), and UUIDv4 resource identifiers.
- Bonus Feature (OpenAPI / Swagger Documentation): Automatically generated interactive API documentation available at /docs (and /redoc).
- Thread-Safe In-Memory Storage: Uses atomic locking and a clean-state reset helper for repeatable, isolated automated testing without database installation overhead.

---

## Quickstart Commands (Automated Reviewer Friendly)

Below are the exact commands to install dependencies, start the server, and execute the automated test suite.

### 1. Install Dependencies

Using a Python virtual environment (Python 3.9+) is recommended:

```bash
# On macOS / Linux:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# On Windows (PowerShell / Command Prompt):
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the Server

Start the FastAPI application using Uvicorn on port 8000:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

- API Base URL: http://localhost:8000
- Interactive Swagger Documentation: http://localhost:8000/docs
- ReDoc API Reference: http://localhost:8000/redoc

### 3. Run the Test Suite

Execute the full automated test suite using pytest:

```bash
pytest
```

To run tests with detailed verbosity and print output:

```bash
pytest -v
```

---

## API Endpoints Reference

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| POST | /expenses | Add a new expense (auto-generates UUIDv4) | 201 Created / 400 Bad Request |
| GET | /expenses | View all expenses (optional query: ?category=Food) | 200 OK |
| GET | /expenses/total | Calculate total expenses (overall and by category) | 200 OK |
| GET | /expenses/{id} | Retrieve a specific expense by ID | 200 OK / 404 Not Found |
| DELETE | /expenses/{id} | Delete an expense by ID | 204 No Content / 404 Not Found |

---

## Repository Structure

```
Diligent-Assignment/
  README.md               # Setup commands, documentation, and API reference
  AI_NOTES.md             # Required AI usage, validation, and rejection notes
  requirements.txt        # Pinned dependencies (fastapi, uvicorn, pydantic, pytest, httpx)
  src/
    __init__.py
    main.py               # FastAPI app initialization, CORS, and custom error middleware
    models.py             # Pydantic schemas with strict field validation
    repository.py         # Thread-safe in-memory storage repository
    routes.py             # REST endpoints and business routing
  tests/
    __init__.py
    test_expenses.py      # Comprehensive test suite (Happy paths + Edge cases)
```

---

## Testing Coverage and Edge Cases Handled

The test suite in tests/test_expenses.py covers 14 distinct scenarios:
1. Happy Paths: Creating expenses, listing all expenses, querying specific UUIDs, and deleting expenses.
2. Category Filtering: Validates case-insensitive filtering (?category=food matches Food and FOOD) and returns empty arrays ([]) for non-matching categories without 404 errors.
3. Floating-Point Precision: Verifies arithmetic precision rounding in /expenses/total to prevent IEEE 754 decimal drift.
4. Error and Input Validation:
   - Rejects negative or zero expense amounts (amount <= 0).
   - Rejects malformed or invalid dates (e.g., 2026-13-45).
   - Rejects empty or whitespace-only strings for title and category.
   - Returns standard HTTP 404 Not Found when requesting or deleting a non-existent UUID.
