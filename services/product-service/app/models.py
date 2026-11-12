from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(300))
    rating = db.Column(db.Float, default=4.0)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description,
                "category": self.category, "price": float(self.price),
                "stock": self.stock, "image_url": self.image_url, "rating": self.rating}

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default="PLACED")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "total": float(self.total), "status": self.status,
                "created_at": self.created_at.strftime("%d %b %Y, %H:%M"),
                "items": [{"name": i.name, "price": float(i.price), "qty": i.qty}
                          for i in self.items]}

class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
