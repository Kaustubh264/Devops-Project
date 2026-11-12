import pytest
from app import create_app

@pytest.fixture(scope="module")
def client():
    app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "TESTING": True})
    with app.test_client() as c:
        yield c

def _register(client, email):
    r = client.post("/api/register", json={"name": "Asha", "email": email, "password": "secret123"})
    return r.get_json()["token"]

def test_order_requires_login(client):
    assert client.post("/api/orders", json={"items": []}).status_code == 401

def test_register_and_login(client):
    _register(client, "a@b.com")
    ok = client.post("/api/login", json={"email": "a@b.com", "password": "secret123"})
    bad = client.post("/api/login", json={"email": "a@b.com", "password": "wrong"})
    assert ok.status_code == 200 and bad.status_code == 401

def test_order_reduces_stock(client):
    h = {"Authorization": "Bearer " + _register(client, "b@b.com")}
    before = client.get("/api/products/1").get_json()["stock"]
    r = client.post("/api/orders", json={"items": [{"product_id": 1, "qty": 2}]}, headers=h)
    assert r.status_code == 201
    assert client.get("/api/products/1").get_json()["stock"] == before - 2
    assert len(client.get("/api/orders", headers=h).get_json()) == 1

def test_cannot_oversell(client):
    h = {"Authorization": "Bearer " + _register(client, "c@b.com")}
    r = client.post("/api/orders", json={"items": [{"product_id": 1, "qty": 99999}]}, headers=h)
    assert r.status_code == 409
