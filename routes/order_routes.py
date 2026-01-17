import uuid
import re
import bcrypt
from db import db
from flask_smorest import Blueprint,abort
from flask.views import MethodView
from schema.order_schema import*
from db.mongo_db import db
import os
from dotenv import load_dotenv,find_dotenv
from flask_jwt_extended import create_access_token,jwt_required,get_jwt,get_jwt_identity
import datetime
from routes.user_routes import user_collection
from routes.product_routes import product_collection

load_dotenv(find_dotenv())
admin_name = os.getenv("ADMINNAME")

#create a blueprint for order
order_app = Blueprint("order",__name__,url_prefix="/orders")

#add a collection
order_collection = db.orders


'''
Route for get order
'''

@order_app.route("/get_orders")
class Get_Order(MethodView):

    @jwt_required()
    @order_app.response(200,OrderSchema(many=True))
    def get(self):
        claims = get_jwt()
        if claims.get("role")!="admin":
            abort(403,message="Admins Only")
        orders = []
        for o in order_collection.find({}):
            order={
                "order_id":o.get("order_id"),
                "user_name":o.get("user_name"),
                "user_id":o.get("user_id"),
                "products":o.get("products"),
                "order_quantity":o.get("order_quantity"),
                "order_price":o.get("order_price"),
                "order_status":o.get("order_status"),
                "payment_status":o.get("payment_status"),
                "payment_method":o.get("payment_method"),
                "shipping_address":o.get("shipping_address"),
                "created_at":o.get("created_at"),
                "reason":o.get("reason"),
                "updated_timestamp":o.get("updated_timestamp")
            }
            if not order["user_name"]==admin_name:

                orders.append(order)


        return orders    
    
@order_app.route("/create_order")
class PostOrder(MethodView):

    @jwt_required()
    @order_app.arguments(PostOrderSchema)
    @order_app.response(201)
    def post(self,data):
        session_user = get_jwt_identity()
        curr_user = data["user_id"]
        user = user_collection.find_one({"user_id":session_user}) 
        if not user:
            abort(404,message="User not found")

        #create order id 
        order_id = str(uuid.uuid4())
        
        #enrich products
        order_price=0
        order_quantity=sum(p["product_quantity"] for p in data["products"])
        enrich_products=[]
        for p in data["products"]:
            product = product_collection.find_one({"sku":p["sku"]})
            if not product:
                abort(404,message="Product not found")
            unit_price = product["product_price"]
            total_price = p["product_quantity"]*unit_price

            enrich_products.append({
                "product_id":product["product_id"],
                "sku":p["sku"],
                "product_name":p["product_name"],
                "product_type":p["product_type"],
                "product_price":unit_price,
                "product_quantity":p["product_quantity"],
                "total_price":total_price
            })
            order_price+=total_price

        #create order time    
        order_created = datetime.datetime.now()

        #insert order
        order_doc = {
            "order_id":order_id,
            "user_name": user["user_name"],
            "user_id": session_user,
            "products":enrich_products,
            "order_quantity":order_quantity,
            "order_price":order_price,
            "order_status":"Pending",
            "payment_status":"Pending",
            "payment_method":data["payment_method"],
            "shipping_address":data["shipping_address"],
            "created_at":order_created
        }    
        result=order_collection.insert_one(order_doc)      
        order_doc.pop("_id",None)

        return {"order_details":order_doc}  

@order_app.route("/cancel_order/<user_id>/<order_id>")
class CancelOrder(MethodView):
    @jwt_required()
    @order_app.arguments(CancelOrderSchema)
    @order_app.response(204)
    def patch(self,data,user_id,order_id):
        
        claims = get_jwt()
        if claims.get("role")=="admin":
            abort(403,message="Only user can delete the order")

        session_user = get_jwt_identity()
        curr_user = user_id
        user = user_collection.find_one({"user_id":session_user}) 
        if not user:
            abort(404,message="User not found")

        order = order_collection.find_one({"order_id":order_id})
        user = user_collection.find_one({"user_id":user_id})

        if not order:
            abort(404,message="Order not found")
        # if not user:
        #     abort(404,message="User not found")   

        # if not bcrypt.checkpw(data["user_password"].encode("utf-8"),user["user_password"].encode("utf-8")):
        #     abort(403,message="Password does not match")    

        # order_collection.delete_one({"order_id":order_id})
        updated_timestamp = datetime.datetime.now()
        order_collection.update_one(
            {"order_id":order_id},
            {"$set":{
                "order_status":"Cancelled",
                "reason":data["reason"],
                "updated_timestamp":updated_timestamp
            }
        })


        return f"order cancelled successfully"     


@order_app.route("/update_quantity/<order_id>/<product_id>")
class Update_Quantity(MethodView):

    @jwt_required()
    @order_app.arguments(UpdateQuantitySchema)
    def patch(self,data,order_id,product_id):
        session_user = get_jwt_identity()
        print(f"session user: {session_user}")
        order = order_collection.find_one({"order_id":order_id,"user_id":session_user})
        if not order:
            abort(404,message="For the given user,there is no such order present")

        shipping_status = order["order_status"]
        if shipping_status=="Delivered":
            abort(403,message="Order has been delivered")
        if shipping_status in ["Shipped", "Cancelled"]:
            abort(403,message=f"Order cannot be updated as it is {shipping_status}")    


        #find product in the given order
        product = None
        for p in order["products"]:
            if p["product_id"]==product_id:
                product=p
                break
        if not product:
            abort(404,message="product not found")

        new_quantity = data["product_quantity"]
        product["product_quantity"] = new_quantity
        product["total_price"] = new_quantity*product["product_price"]

        order_quantity = sum(p["product_quantity"] for p in order["products"])
        order_price = sum(p["total_price"] for p in order["products"])            

        updated_timestamp = datetime.datetime.now()

        order_collection.update_one(
            {"order_id": order_id},
            {"$set": {
                "products": order["products"],
                "order_quantity": order_quantity,
                "order_price": order_price,
                "updated_timestamp": updated_timestamp
            }}
        )

        # return updated order
        updated_order = order_collection.find_one({"order_id": order_id})
        updated_order.pop("_id", None)
        return updated_order


@order_app.route("/update_shipping_address/<order_id>")
class Update_Address(MethodView):
    @jwt_required()
    @order_app.arguments(UpdateAddressSchema)
    def patch(self,data,order_id):
        session_user = get_jwt_identity()
        print(f"session user: {session_user}")
        order = order_collection.find_one({"order_id":order_id,"user_id":session_user})
        if not order:
            abort(404,message="For the given user,there is no such order present")

        shipping_status = order["order_status"]
        if shipping_status=="Delivered":
            abort(403,message="Order has been delivered")
        if shipping_status=="Cancelled":
            abort(403,message=f"Order cannot be updated as it is {shipping_status}")    


        #update the shipping address
        current_address = order["shipping_address"]
        updated_address = data["update_shipping_address"]

        updated_timestamp = datetime.datetime.now()

        order_collection.update_one(
            {"order_id": order_id},
            {"$set": {
                "shipping_address": updated_address,
                "updated_timestamp": updated_timestamp
            }}
        )

        # return updated order
        updated_order = order_collection.find_one({"order_id": order_id})
        updated_order.pop("_id", None)
        return updated_order
    

@order_app.route("/user_status/<user_id>")
class UserOrderStatus(MethodView):
       @jwt_required()
       def get(self,user_id):
        current_user = get_jwt_identity()

        if current_user!=user_id:
            abort(403,message="User ID does not match with the session user")
        orders = list(order_collection.find({"user_id":current_user}))
        if not orders:
            return "No orders placed yet"
        for o in orders:
            o.pop("_id",None)
        return orders,200
        