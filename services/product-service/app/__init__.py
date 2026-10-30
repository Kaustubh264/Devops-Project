import logging
import sys
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics
from .config import Config
from .models import db, Product
from .routes import bp

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
            db.session.add_all([
                Product(name="Laptop", price=55000, stock=25),
                Product(name="Headphones", price=2500, stock=100),
                Product(name="Keyboard", price=1500, stock=60),
            ])
            db.session.commit()
    return app
