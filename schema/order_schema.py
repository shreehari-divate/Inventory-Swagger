from marshmallow import Schema,fields,validate
# from marshmallow_enum import EnumField
import enum

class ProductInOrderSchema(Schema):
    product_id = fields.Str(required=True)
    sku = fields.Str(required=True)
    product_name = fields.Str(required=True)
    product_type = fields.Str(required=True)
    product_quantity = fields.Int(required=True)
    product_price = fields.Int(required=True)
    total_price = fields.Int(required=True)

class ProductPostOrderSchema(Schema):
    sku = fields.Str(required=True)
    product_name = fields.Str(required=True)
    product_type = fields.Str(required=True)
    product_quantity = fields.Int(required=True)


class OrderSchema(Schema):

    order_id = fields.Str(required=True)
    user_name = fields.Str(required=True)
    user_id = fields.Str(required=True)

    products = fields.List(fields.Nested(ProductInOrderSchema),required=True)
    order_quantity = fields.Int(required=True)
    order_price = fields.Float(required=True)
    order_status = fields.Str(required=True,validate=validate.OneOf(["Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"]))

    payment_status = fields.Str(required=True,validate=validate.OneOf(["Pending", "Paid", "Refunded"]))  
    payment_method = fields.Str(required=True,validate=validate.OneOf(["Credit Card", "Debit Card", "UPI", "NetBanking", "CashOnDelivery"]))
    shipping_address = fields.Str(required=True)

    created_at = fields.DateTime()

    reason = fields.Str()
    updated_timestamp = fields.DateTime()


class PostOrderSchema(OrderSchema):
    class Meta():
        exclude=("order_id","user_name","order_price","order_status","payment_status","created_at","order_quantity")    
    products = fields.List(fields.Nested(ProductPostOrderSchema),required=True)


class CancelOrderSchema(Schema):
    # order_id = fields.Str(required=True)
    # user_id = fields.Str()
    # user_name = fields.Str(required=True)
    reason = fields.Str(required=True)
    # user_password = fields.Str(required=True)

class UpdateQuantitySchema(Schema):
    product_quantity = fields.Int(required=True, validate=validate.Range(min=1))    

class UpdateAddressSchema(Schema):
    update_shipping_address = fields.Str(required=True)    
