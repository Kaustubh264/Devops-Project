import logging
from flask import Blueprint, jsonify, request
from sqlalchemy import text
from .models import db, Product

bp = Blueprint("api", __name__)
log = logging.getLogger("product-service")

@bp.get("/health")
def health():
    return jsonify(status="ok")

@bp.get("/ready")
def ready():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ready")
    except Exception:
        log.exception("database not reachable")
        return jsonify(status="db down"), 503

@bp.get("/api/products")
def list_products():
    return jsonify([p.to_dict() for p in Product.query.all()])

@bp.get("/api/products/<int:pid>")
def get_product(pid):
    p = db.session.get(Product, pid)
    if not p:
        return jsonify(error="product not found"), 404
    return jsonify(p.to_dict())

@bp.post("/api/products")
def create_product():
    data = request.get_json(silent=True) or {}
    try:
        name = data["name"]
        price = float(data["price"])
        stock = int(data.get("stock", 0))
        if not name or price < 0 or stock < 0:
            raise ValueError
    except (KeyError, ValueError, TypeError):
        return jsonify(error="name, price (>=0), stock (>=0) required"), 400
    p = Product(name=name, price=price, stock=stock)
    db.session.add(p)
    db.session.commit()
    log.info("product created id=%s", p.id)
    return jsonify(p.to_dict()), 201
