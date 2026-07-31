import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.repository import repository

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_repository():
    """
    Ensure each test runs against a clean state.
    """
    repository.clear()
    yield
    repository.clear()


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_create_expense_success():
    payload = {
        "title": "Grocery Shopping",
        "amount": 45.50,
        "category": "Food",
        "date": "2026-07-31"
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert len(data["id"]) > 0
    assert data["title"] == payload["title"]
    assert data["amount"] == payload["amount"]
    assert data["category"] == payload["category"]
    assert data["date"] == payload["date"]


def test_get_all_expenses():
    payload1 = {"title": "Lunch", "amount": 15.0, "category": "Food", "date": "2026-07-30"}
    payload2 = {"title": "Bus Ticket", "amount": 2.5, "category": "Travel", "date": "2026-07-31"}
    client.post("/expenses", json=payload1)
    client.post("/expenses", json=payload2)

    response = client.get("/expenses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_filter_expenses_by_category_case_insensitive():
    payload1 = {"title": "Lunch", "amount": 15.0, "category": "Food", "date": "2026-07-30"}
    payload2 = {"title": "Dinner", "amount": 25.0, "category": "food", "date": "2026-07-31"}
    payload3 = {"title": "Bus Ticket", "amount": 2.5, "category": "Travel", "date": "2026-07-31"}
    client.post("/expenses", json=payload1)
    client.post("/expenses", json=payload2)
    client.post("/expenses", json=payload3)

    # Filter by lowercase 'food' should match both 'Food' and 'food'
    response = client.get("/expenses?category=food")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for item in data:
        assert item["category"].lower() == "food"


def test_filter_expenses_empty_result():
    response = client.get("/expenses?category=NonExistentCategory")
    assert response.status_code == 200
    assert response.json() == []


def test_calculate_total_expenses_precision():
    # Adding floating-point numbers that typically cause precision issues in Python
    client.post("/expenses", json={"title": "Item 1", "amount": 10.20, "category": "Food", "date": "2026-07-31"})
    client.post("/expenses", json={"title": "Item 2", "amount": 20.10, "category": "Food", "date": "2026-07-31"})
    client.post("/expenses", json={"title": "Taxi", "amount": 50.00, "category": "Travel", "date": "2026-07-31"})

    response = client.get("/expenses/total")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 80.30
    assert data["by_category"] == {
        "Food": 30.30,
        "Travel": 50.00
    }


def test_get_expense_by_id_success_and_not_found():
    created = client.post("/expenses", json={
        "title": "Book", "amount": 12.99, "category": "Education", "date": "2026-07-31"
    }).json()
    expense_id = created["id"]

    # Success get
    response = client.get(f"/expenses/{expense_id}")
    assert response.status_code == 200
    assert response.json()["id"] == expense_id

    # Non-existent get
    not_found = client.get("/expenses/non-existent-uuid")
    assert not_found.status_code == 404


def test_delete_expense_success_and_not_found():
    created = client.post("/expenses", json={
        "title": "Coffee", "amount": 4.50, "category": "Food", "date": "2026-07-31"
    }).json()
    expense_id = created["id"]

    # Success delete
    delete_res = client.delete(f"/expenses/{expense_id}")
    assert delete_res.status_code == 204

    # Confirm deleted
    assert client.get(f"/expenses/{expense_id}").status_code == 404

    # Delete non-existent ID
    assert client.delete("/expenses/non-existent-id").status_code == 404


def test_create_expense_invalid_negative_amount():
    response = client.post("/expenses", json={
        "title": "Bad Expense", "amount": -10.0, "category": "Food", "date": "2026-07-31"
    })
    assert response.status_code == 400
    assert "error" in response.json()


def test_create_expense_invalid_zero_amount():
    response = client.post("/expenses", json={
        "title": "Bad Expense", "amount": 0.0, "category": "Food", "date": "2026-07-31"
    })
    assert response.status_code == 400


def test_create_expense_invalid_date_format():
    response = client.post("/expenses", json={
        "title": "Bad Date", "amount": 10.0, "category": "Food", "date": "2026-13-45"
    })
    assert response.status_code == 400


def test_create_expense_empty_title():
    response = client.post("/expenses", json={
        "title": "   ", "amount": 10.0, "category": "Food", "date": "2026-07-31"
    })
    assert response.status_code == 400


def test_create_expense_missing_required_field():
    response = client.post("/expenses", json={
        "title": "No Amount", "category": "Food", "date": "2026-07-31"
    })
    assert response.status_code == 400
