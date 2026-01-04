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
order_collection = db.users


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
                "shipping_address":o.get("shipping_address")
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
        order_quantity=0
        enrich_products=[]
        for p in data["products"]:
            product = product_collection.find_one({"sku":p["sku"]})
            if not product:
                abort(404,message="Product not found")
            unit_price = product["product_price"]
            total_price = data["order_quantity"]*unit_price

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
            order_quantity+=p["product_quantity"]

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

        return {"order created at": order_created,"order_details":order_doc}  

