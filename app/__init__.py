from flask import Flask
from app.extensions import db, ma, migrate, limiter, cache


# blueprint imports
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.customers.routes import customers_bp
# ISSUE: Removed debug print statements - these shouldn't be in production code
from app.blueprints.inventory import inventory_bp


def create_app(config_class="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # init extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cache.init_app(app)

    app.register_blueprint(mechanics_bp)
    app.register_blueprint(service_tickets_bp)
    app.register_blueprint(customers_bp)
    # ISSUE: Removed debug print statements - these shouldn't be in production code
    app.register_blueprint(inventory_bp, url_prefix="/parts")
    return app
