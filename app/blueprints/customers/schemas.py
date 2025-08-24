from app.models import Customer
from app.extensions import ma
from marshmallow import fields

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        include_fk = True   

    
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    # ISSUE: Changed back to Email field type for proper email validation
    email = fields.Email(required=True)
    # ISSUE: Made phone optional because the model allows it to be nullable
    # If you want phone to be required, change the model to nullable=False
    phone = fields.Str(required=False)   
    car = fields.Str(required=False)   

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)