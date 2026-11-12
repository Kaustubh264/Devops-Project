import logging
import sys
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics
from .config import Config
from .models import db, Product
from .routes import bp

SEED = [
    ("UltraBook 14 Laptop", "14-inch FHD, 16GB RAM, 512GB SSD", "Electronics", 55000, 25, "laptop", 4.5),
    ("Wireless Headphones", "Noise cancelling, 30-hour battery", "Electronics", 2499, 100, "headphones", 4.3),
    ("Mechanical Keyboard", "RGB backlit, blue switches", "Electronics", 3499, 60, "keyboard", 4.6),
    ("Smart Watch", "Heart-rate, SpO2 and sleep tracking", "Electronics", 4999, 40, "smartwatch", 4.1),
    ("Running Shoes", "Lightweight, breathable mesh", "Fashion", 2999, 80, "shoes", 4.4),
    ("Travel Backpack", "35L, water resistant, laptop sleeve", "Fashion", 1499, 55, "backpack", 4.2),
    ("Coffee Maker", "12-cup programmable brewer", "Home", 3999, 20, "coffee", 4.0),
    ("LED Desk Lamp", "Dimmable, USB charging port", "Home", 899, 70, "lamp", 4.3),
    ("Python Programming Book", "Beginner to advanced, 600 pages", "Books", 599, 150, "book", 4.7),
]

def create_app(overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    logging.basicConfig(
        level=logging.INFO, stream=sys.stdout,
        format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}')

    db.init_app(app)
    PrometheusMetrics(app)
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            for i, (name, desc, cat, price, stock, kw, rating) in enumerate(SEED, 1):
                db.session.add(Product(
                    name=name, description=desc, category=cat, price=price,
                    stock=stock, rating=rating,
                    image_url=f"https://loremflickr.com/400/300/{kw}?lock={i}"))
            db.session.commit()
    return app
