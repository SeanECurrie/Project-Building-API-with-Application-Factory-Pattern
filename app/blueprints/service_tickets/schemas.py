from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True

    id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    # ISSUE: The model doesn't have a 'status' field, so I removed it
    # The model has: description, date, customer_id
    # If you want to add status later, you need to add it to the model first

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)

