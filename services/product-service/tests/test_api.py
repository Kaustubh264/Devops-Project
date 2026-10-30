import pytest
from app import create_app

@pytest.fixture(scope="module")
def client():
    app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "TESTING": True})
    with app.test_client() as c:
        yield c

def test_health(client):
    assert client.get("/health").status_code == 200

def test_ready(client):
    assert client.get("/ready").status_code == 200

def test_list_products(client):
    r = client.get("/api/products")
    assert r.status_code == 200 and len(r.get_json()) >= 3

def test_create_product(client):
    r = client.post("/api/products", json={"name": "Mouse", "price": 799, "stock": 10})
    assert r.status_code == 201

def test_invalid_product(client):
    assert client.post("/api/products", json={}).status_code == 400

def test_not_found(client):
    assert client.get("/api/products/9999").status_code == 404
