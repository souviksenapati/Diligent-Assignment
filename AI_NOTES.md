# AI Collaboration and Engineering Notes (AI_NOTES.md)

This document details the intentional use of AI tools (such as Claude 3.5 Sonnet / Gemini 3.1 Pro) during the development of the Smart Expense Tracker API, following Diligent Corporation's evaluation rubric.

---

## 1. AI-Generated Code vs. Handwritten Code

### AI-Assisted Components
- Pydantic Model Skeleton (src/models.py): Used AI to scaffold the initial BaseModel structures (ExpenseCreate, Expense, and TotalResponse) and generate JSON Schema example blocks for OpenAPI documentation.
- Test Boilerplate (tests/test_expenses.py): Leveraged AI to generate repetitive HTTP client test payloads and assertions across multiple validation scenarios (e.g., negative amounts, malformed date strings, empty fields).

### Handwritten and Manually Engineered Components
- Thread-Safe Repository Architecture (src/repository.py): Designed and implemented the in-memory storage layer using threading.RLock() to guarantee thread safety during concurrent operations and added an atomic clear() helper to ensure test isolation.
- Custom Validation and Exception Handling (src/main.py and src/models.py): Wrote custom Pydantic @field_validator hooks to strip whitespace and prevent blank/empty string submissions. Implemented a custom RequestValidationError exception handler in FastAPI to return RFC-7807/standardized JSON error bodies ({"error": "...", "detail": ..., "code": 400}) instead of default unhandled stack traces.
- Floating-Point Arithmetic Precision and Casing Normalization (src/repository.py): Handled decimal rounding (round(..., 2)) to prevent IEEE 754 precision drift when summing float values, and engineered case-insensitive category grouping that preserves clean display names.

---

## 2. What I Validated, Tested, and Modified in AI Output

### A. Preventing Floating-Point Precision Drift in Total Calculations
- AI Output: The AI suggested calculating total sums using basic generator expressions:
  total = sum(item.amount for item in self._store.values())
- Why and How I Changed It: In Python, floating-point arithmetic can produce precision drift (e.g., 10.20 + 20.10 = 30.299999999999997). I modified the totals calculation in src/repository.py to apply explicit round(..., 2) precision formatting across both overall totals and category breakdowns. I added test_calculate_total_expenses_precision in tests/test_expenses.py to prove accurate decimal summation.

### B. Case-Insensitive Category Filtering and Grouping
- AI Output: The AI initially generated an exact string match for filtering (if e.category == category:) and grouped categories in /expenses/total by their raw string keys.
- Why and How I Changed It: Real users might submit "Food", "food", or "FOOD". An exact match breaks user intuition. I modified get_all() to normalize both the query and stored category strings using .strip().lower(). For /expenses/total, I implemented a mapping layer that groups categories case-insensitively while preserving the first-seen clean display name (e.g., grouping both "food" and "Food" under "Food").

### C. Standardizing HTTP 400 vs. 422 Error Status Codes
- AI Output: By default, FastAPI throws HTTP 422 Unprocessable Entity for schema validation errors with verbose internal field paths.
- Why and How I Changed It: Enterprise REST APIs should return clean 400 Bad Request responses for malformed client input. I added a custom @app.exception_handler(RequestValidationError) in src/main.py that intercepts validation errors and returns a clean, standardized 400 Bad Request JSON payload.

---

## 3. AI Suggestions I Decided Not to Use and Why

### A. Rejected: SQLAlchemy + SQLite / ORM Persistence
- AI Suggestion: The AI suggested adding SQLAlchemy and an SQLite database file (expenses.db) to persist data across server restarts.
- Why Rejected: The assignment instructions explicitly state: "Data can be stored in memory or a local JSON file; no database is required." Adding an ORM introduces unnecessary dependency bloat, potential file-permission errors in automated CI/CD container grading, and database lock contention during concurrent test execution. A thread-safe in-memory repository is cleaner, faster, and 100% compliant.

### B. Rejected: Over-Engineered Regular Expressions for Date Validation
- AI Suggestion: The AI suggested adding regex validators (^\d{4}-\d{2}-\d{2}$) to validate the date field.
- Why Rejected: Regex date validation is brittle and fails to catch impossible dates like 2026-02-31. I rejected the regex and instead utilized Python's native datetime.date type within Pydantic. Pydantic automatically parses ISO-8601 strings and validates calendar correctness out-of-the-box.

### C. Rejected: Returning 404 Not Found for Empty Filter Queries
- AI Suggestion: In the category filter endpoint (GET /expenses?category=...), the AI suggested raising an HTTPException(status_code=404) if no expenses matched the category.
- Why Rejected: In RESTful API design, querying a collection resource with a valid filter that yields zero results should return an empty list [] with 200 OK, not a 404 Not Found. 404 should be reserved for requesting non-existent specific resource IDs (GET /expenses/{id}).
