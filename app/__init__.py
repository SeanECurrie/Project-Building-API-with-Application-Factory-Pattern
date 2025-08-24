from flask import Flask, render_template
from app.extensions import db, ma, migrate, limiter, cache
from app.models import Mechanic, Customer, ServiceTicket, Inventory


# blueprint imports
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.customers.routes import customers_bp
# ISSUE: Removed debug print statements - these shouldn't be in production code
from app.blueprints.inventory import inventory_bp


def create_app(config_class="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Set Flask run configuration
    app.config['FLASK_RUN_HOST'] = '127.0.0.1'
    app.config['FLASK_RUN_PORT'] = 5001

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
    
    @app.route("/")
    def home():
        mechanics = Mechanic.query.all()
        customers = Customer.query.all()
        tickets = ServiceTicket.query.all()
        inventory = Inventory.query.all()
        return render_template(
            "home.html",
            mechanics=mechanics,
            customers=customers,
            tickets=tickets,
            inventory=inventory,
        )

    return app
