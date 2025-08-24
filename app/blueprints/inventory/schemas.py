# ISSUE: Was using marshmallow_sqlalchemy instead of flask_marshmallow
# This caused inconsistency with other blueprints and potential import errors
from app.extensions import ma
from app.models import Inventory, ServiceTicketInventory

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True

class ServiceTicketInventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicketInventory
        load_instance = True

# for singular or lis
inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)

service_ticket_inventory_schema = ServiceTicketInventorySchema()
service_ticket_inventories_schema = ServiceTicketInventorySchema(many=True)
