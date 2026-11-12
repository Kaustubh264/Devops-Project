import logging
from flask import Blueprint, jsonify, request, current_app, send_from_directory
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, Product, User, Order, OrderItem

bp = Blueprint("api", __name__)
log = logging.getLogger("shopkart")

def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

def _current_user():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    try:
        uid = _serializer().loads(header[7:], max_age=86400)
    except (BadSignature, SignatureExpired):
        return None
    return db.session.get(User, uid)

@bp.get("/")
def index():
    return send_from_directory(current_app.static_folder, "index.html")

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
    return jsonify([p.to_dict() for p in Product.query.order_by(Product.id).all()])

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
    p = Product(name=name, price=price, stock=stock,
                description=data.get("description"), category=data.get("category"),
                image_url=data.get("image_url"))
    db.session.add(p)
    db.session.commit()
    log.info("product created id=%s", p.id)
    return jsonify(p.to_dict()), 201

@bp.post("/api/register")
def register():
    d = request.get_json(silent=True) or {}
    name = str(d.get("name", "")).strip()
    email = str(d.get("email", "")).strip().lower()
    password = str(d.get("password", ""))
    if not name or "@" not in email or len(password) < 6:
        return jsonify(error="name, valid email and password (min 6 chars) required"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="email already registered"), 409
    u = User(name=name, email=email, password_hash=generate_password_hash(password))
    db.session.add(u)
    db.session.commit()
    log.info("user registered id=%s", u.id)
    return jsonify(token=_serializer().dumps(u.id), name=u.name), 201

@bp.post("/api/login")
def login():
    d = request.get_json(silent=True) or {}
    email = str(d.get("email", "")).strip().lower()
    u = User.query.filter_by(email=email).first()
    if not u or not check_password_hash(u.password_hash, str(d.get("password", ""))):
        return jsonify(error="invalid email or password"), 401
    return jsonify(token=_serializer().dumps(u.id), name=u.name)

@bp.post("/api/orders")
def create_order():
    user = _current_user()
    if not user:
        return jsonify(error="login required"), 401
    items = (request.get_json(silent=True) or {}).get("items")
    if not isinstance(items, list) or not items:
        return jsonify(error="items required"), 400
    lines = []
    try:
        for it in items:
            pid, qty = int(it["product_id"]), int(it["qty"])
            if qty < 1:
                raise ValueError
            p = db.session.get(Product, pid, with_for_update=True)
            if not p:
                db.session.rollback()
                return jsonify(error=f"product {pid} not found"), 404
            if p.stock < qty:
                db.session.rollback()
                return jsonify(error=f"only {p.stock} left for {p.name}"), 409
            p.stock -= qty
            lines.append(OrderItem(product_id=p.id, name=p.name,
                                   price=float(p.price), qty=qty))
    except (KeyError, ValueError, TypeError):
        db.session.rollback()
        return jsonify(error="each item needs product_id and qty (>=1)"), 400
    order = Order(user_id=user.id, items=lines,
                  total=sum(l.price * l.qty for l in lines))
    db.session.add(order)
    db.session.commit()
    log.info("order placed id=%s user=%s", order.id, user.id)
    return jsonify(order.to_dict()), 201

@bp.get("/api/orders")
def my_orders():
    user = _current_user()
    if not user:
        return jsonify(error="login required"), 401
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.id.desc()).all()
    return jsonify([o.to_dict() for o in orders])
