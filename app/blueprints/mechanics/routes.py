from flask import request, jsonify, current_app, render_template
from functools import wraps
from datetime import datetime, timedelta, timezone

from . import mechanics_bp
from app.extensions import db
from app.models import Mechanic, ServiceTicket, ticket_mechanics, Customer, Inventory
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema, login_schema

from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from jose import jwt, JWTError
from sqlalchemy import func, desc
from .schemas import mechanic_schema, mechanics_schema

@mechanics_bp.route("/ui", methods=["GET"])
def api_demo():
    """Simple UI showing available API endpoints and data"""
    try:
        mechanics = Mechanic.query.all()
        customers = Customer.query.all()
        tickets = ServiceTicket.query.all()
        inventory = Inventory.query.all()
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mechanic Shop API - Available Routes</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }}
                .endpoint {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .method {{ font-weight: bold; color: #fff; padding: 5px 10px; border-radius: 3px; }}
                .get {{ background: #61affe; }}
                .post {{ background: #49cc90; }}
                .put {{ background: #fca130; }}
                .delete {{ background: #f93e3e; }}
                .data-section {{ margin: 20px 0; }}
                .count {{ font-size: 24px; font-weight: bold; color: #333; }}
            </style>
        </head>
        <body>
            <h1>🔧 Mechanic Shop API - Available Routes</h1>
            
            <div class="data-section">
                <h2>📊 Current Database Status</h2>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; text-align: center;">
                    <div>
                        <div class="count">{len(mechanics)}</div>
                        <div>Mechanics</div>
                    </div>
                    <div>
                        <div class="count">{len(customers)}</div>
                        <div>Customers</div>
                    </div>
                    <div>
                        <div class="count">{len(tickets)}</div>
                        <div>Service Tickets</div>
                    </div>
                    <div>
                        <div class="count">{len(inventory)}</div>
                        <div>Inventory Items</div>
                    </div>
                </div>
            </div>

            <h2>🚀 Available API Endpoints</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/mechanics/ui</strong> - This page
                <br><small>Shows API documentation and current data</small>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/mechanics/ping</strong> - Health check
                <br><small>Returns: {{"ok": true}}</small>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/mechanics/</strong> - List all mechanics
                <br><small>Returns: Array of mechanic objects</small>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/mechanics/</strong> - Create new mechanic
                <br><small>Body: {{"name": "string", "email": "string", "specialty": "string", "password": "string"}}</small>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/mechanics/login</strong> - Mechanic login
                <br><small>Body: {{"name": "string", "password": "string"}}</small>
                <br><small>Returns: JWT token for authentication</small>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/customers/</strong> - List all customers
                <br><small>Returns: Array of customer objects</small>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/customers/</strong> - Create new customer
                <br><small>Body: {{"name": "string", "email": "string", "phone": "string", "car": "string"}}</small>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/tickets/</strong> - List all service tickets
                <br><small>Returns: Array of service ticket objects</small>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/tickets/</strong> - Create new service ticket
                <br><small>Body: {{"description": "string", "date": "string", "customer_id": "integer"}}</small>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/parts/</strong> - List all inventory items
                <br><small>Returns: Array of inventory objects</small>
            </div>

            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/parts/</strong> - Create new inventory item
                <br><small>Body: {{"name": "string", "description": "string", "quantity": "integer", "price": "float"}}</small>
            </div>

            <h2>🔑 Authentication</h2>
            <p>Most endpoints require a JWT token in the Authorization header:</p>
            <code>Authorization: Bearer &lt;your_jwt_token&gt;</code>
            
            <h2>📝 Test with Postman</h2>
            <p>Use these endpoints in Postman to test your API functionality!</p>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1><p>This proves the API needs fixing!</p>"

# ---------------- JWT helper ----------------
def encode_token(mechanic_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(mechanic_id),                     # subject must be a string
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=7)).timestamp()),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


# --------------- token_required ---------------
def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )
            request.mechanic_id = int(payload.get("sub"))
        except JWTError:
            return jsonify({"error": "Invalid or expired token"}), 401

        return fn(*args, **kwargs)
    return wrapper


# ---------------- Mechanics routes ----------------
@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    try:
        mech = mechanic_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400


    if "password" in request.json:
        mech.set_password(request.json["password"])

    try:
        db.session.add(mech)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409

    return mechanic_schema.jsonify(mech), 201


@mechanics_bp.route("/", methods=["GET"])
def get_mechanics():
    mechs = Mechanic.query.all()
    return mechanics_schema.jsonify(mechs), 200


@mechanics_bp.route("/login", methods=["POST"])
def login():
    try:
        creds = login_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # look up by mechanic name
    mech = Mechanic.query.filter_by(name=creds["name"]).first()

    # check against plain-text password for now
    if mech and mech.check_password(creds["password"]):
        token = encode_token(mech.id)
        return jsonify({"token": token}), 200

    return jsonify({"error": "Invalid name or password"}), 401


# ---- protected: update/delete self ----
@mechanics_bp.route("/<int:id>", methods=["PUT"])
@token_required
def update_mechanic(id):
    if request.mechanic_id != id:
        return jsonify({"error": "Forbidden: you can only update your own profile"}), 403

    mech = Mechanic.query.get_or_404(id)
    data = request.json or {}
    if "name" in data:
        mech.name = data["name"]
    if "specialty" in data:
        mech.specialty = data["specialty"]
    if "password" in data and data["password"]:
        mech.set_password(data["password"])
    db.session.commit()
    return mechanic_schema.jsonify(mech), 200


@mechanics_bp.route("/<int:id>", methods=["DELETE"])
@token_required
def delete_mechanic(id):
    if request.mechanic_id != id:
        return jsonify({"error": "Forbidden: you can only delete your own profile"}), 403

    mech = Mechanic.query.get_or_404(id)
    db.session.delete(mech)
    db.session.commit()
    return jsonify({"message": f"Mechanic {id} deleted"}), 200


@mechanics_bp.route("/my-tickets", methods=["GET"])
@token_required
def my_tickets():
    # admin passes 
    mech_id = request.args.get("mechanic_id") or (request.json.get("mechanic_id") if request.is_json else None)

    if not mech_id:
        mech_id = request.mechanic_id  

    tickets = (
        ServiceTicket.query.join(ticket_mechanics)
        .filter(ticket_mechanics.c.mechanic_id == mech_id)
        .all()
    )
    return jsonify([
        {"id": t.id, "description": t.description, "status": t.status}
        for t in tickets
    ]), 200

# === HOMEWORK ADDITION: Mechanic(s) with most tickets ===
@mechanics_bp.route("/top", methods=["GET"])
@token_required
def mechanic_with_most_tickets():
    result = (
        db.session.query(
            Mechanic.id,
            Mechanic.name,
            Mechanic.email,
            func.count(ticket_mechanics.c.ticket_id).label("ticket_count")
        )
        .join(ticket_mechanics, Mechanic.id == ticket_mechanics.c.mechanic_id)
        .group_by(Mechanic.id)
        .order_by(desc("ticket_count"))
        .first()
    )

    if not result:
        return jsonify({"message": "No mechanics found"}), 404

    return jsonify({
        "id": result.id,
        "name": result.name,
        "email": result.email,
        "ticket_count": int(result.ticket_count)
    }), 200

@mechanics_bp.route("/ticket-count", methods=["GET"])
@token_required
def mechanics_by_ticket_count():
    rows = (
        db.session.query(
            Mechanic.id,
            Mechanic.name,
            Mechanic.email,
            func.count(ticket_mechanics.c.ticket_id).label("ticket_count")
        )
        .join(ticket_mechanics, Mechanic.id == ticket_mechanics.c.mechanic_id)
        .group_by(Mechanic.id)
        .order_by(desc("ticket_count"))
        .all()
    )

    return jsonify([
        {
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "ticket_count": int(r.ticket_count)
        }
        for r in rows
    ]), 200
