import uuid
import re
import bcrypt
from db import db
from flask_smorest import Blueprint,abort
from flask.views import MethodView
from schema.product_schema import *
from db.mongo_db import db
import os
from dotenv import load_dotenv,find_dotenv
from flask_jwt_extended import create_access_token,jwt_required,get_jwt
from datetime import datetime
from bson import ObjectId

prouct_app = Blueprint("product","__name__",url_prefix="/product")

product_collection = db.products

# product_collection.delete_many({})

'''
Get product details
'''

@prouct_app.route("/get_products")
class Get_Product(MethodView):

    @jwt_required()
    @prouct_app.response(200)
    def get(self):
        claims = get_jwt()
        is_admin = claims.get("role")=="admin"
        
        products = list(product_collection.find({}))
        for p in products:
            p["_id"] = str(p["_id"])
            if not is_admin:
                p.pop("_id",None)
                p.pop("product_id",None)
                p.pop("timestamp")
        return products
    

'''
Add Products
'''

@prouct_app.route("/add_products")
class Add_Product(MethodView):

    @prouct_app.arguments(Add_Product_Schema)
    @prouct_app.response(201)
    def post(self,data):

        #create product id
        product_id = str(uuid.uuid4())

        #product_type:
        prd_type = data["product_type"]
        # if not product_collection.find_one({"product_type":prd_type}):
        #     abort(404,message="No such product type exists")

        #product name
        prd_name = data["product_name"]
        # if product_collection.find_one({"product_name":prd_name}):
        #     abort(400,message="This product already exsits, please update the quantity else add other product name")

        #product price
        prd_price = data["product_price"]

        #quantity
        prd_quantity = data["quantity_present"]

        #active status
        prd_status = data["is_active"]

        #sku-stock keeping unit
        sku = data["sku"]
        if product_collection.find_one({"sku":sku}):
            abort(400,message="sku exists")

        #timestamp
        tn = datetime.now()
        tmst = tn

        #product decription
        prod_dec = data["product_desc"]

        #add the above data to the db
        product_to_be_inserted = {
            "product_id":product_id,
            "product_type":prd_type,
            "product_name":prd_name,
            "product_desc":prod_dec,
            "product_price":prd_price,
            "quantity_present":prd_quantity,
            "is_active":prd_status,
            "sku":sku,
            "timestamp":tmst
        }   
        product_collection.insert_one(product_to_be_inserted)

        return {"id":product_id,
                "product_type":prd_type,
                "product_name":prd_name
        }

'''
Delete the product 
'''
@prouct_app.route("/delete_product/<product_id>")
class Delete_Product(MethodView):
    @prouct_app.response(201)
    def delete(self,product_id):
        
        prod_id = str(product_id)

        if not product_collection.find_one({"product_id":prod_id}):
            abort(404,message="Product not found")

        product_collection.delete_one({"product_id":product_id})
        return "Product deleted successfully"    

'''
Update the product
'''    
@prouct_app.route("/update_product/<product_id>")
class Update_Products(MethodView):
    @prouct_app.arguments(Update_Product_Schema)
    @prouct_app.response(201)
    def put(self,data,product_id):
        
        if not product_collection.find_one({"product_id":product_id}):
            abort(404,message="Product does not exists")

        product_collection.update_one(
            {"product_id":product_id},
            {"$set":{
                "product_name":data["product_name"],
                "product_desc":data["product_desc"],
                "product_price":data["product_price"],
                "quantity_present":data["quantity_present"],
                "is_active":data["is_active"],
                "sku":data["sku"]
            }}
        ) 
        return "product updated"
     

@prouct_app.route("/update/<product_id>/<quantity_present>/<product_price>/<is_active>")
class Update_Product(MethodView):
    @prouct_app.response(201)
    def patch(self,product_id,quantity_present,product_price,is_active):
        
        if not product_collection.find_one({"product_id":product_id}):
            abort(404,message="Product does not exists")

        product = product_collection.find_one( {
            "product_id": product_id}, 
             {"_id": 0, 
              "product_price": 1, 
              "quantity_present": 1, 
              "is_active": 1}
                )

        old_price = product["product_price"]
        old_quantity = product["quantity_present"]
        old_is_active = product["is_active"]

        product_collection.update_one(
            {"product_id":product_id},
            {"$set":{
                "product_price":product_price,
                "quantity_present":quantity_present,
                "is_active":is_active
            }}
        ) 
        return {"old_price":old_price,
                "new_price":product_price,
                "old_quantity":old_quantity,
                "new_quantity":quantity_present,
                "old_active_status":old_is_active,
                "new_active_status":is_active}    
    
