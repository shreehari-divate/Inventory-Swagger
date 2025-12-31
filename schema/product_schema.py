from marshmallow import Schema,fields,validate
# from marshmallow_enum import EnumField
import enum

class Product_Types(enum.Enum):
    LAPTOP = "Lpatop"
    SMARTPHONE = "Smartphone"
    TV = "TV"
    REFRIGRATOR = "Refrigrator"
    WASHINGMACHINE = "Washingmachine"


class Product_Schema(Schema):
    product_id = fields.Str()
    product_type = fields.Str(required=True,validate=validate.OneOf(["Laptop", "Smartphone", "TV", "Refrigerator", "WashingMachine"]))
    product_name = fields.Str(required=True)
    product_desc = fields.Str(required=True)
    product_price = fields.Float(required=True)
    quantity_present = fields.Int(required=True)
    is_active = fields.Bool(required=True)
    sku = fields.Str(required=True)
    timestamp = fields.DateTime()
     

class Add_Product_Schema(Product_Schema):
    class Meta:
        exclude=("product_id","timestamp")


class Update_Product_Schema(Product_Schema):
    class Meta:
        exclude=("product_id","timestamp","product_type")
    
    
    