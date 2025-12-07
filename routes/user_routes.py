import uuid
import re
import bcrypt
from db import db
from flask_smorest import Blueprint,abort
from flask.views import MethodView
from schema.user_schema import User_Schema,User_Create_Schema
from db.mongo_db import db
import os
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

admin_name = os.getenv("ADMINNAME")
admin_password = os.getenv("ADMINPASSWORD")
admin_id = os.getenv("ADMINID")
user_app = Blueprint("user","__name__",url_prefix="/user")

#user collection
user_collection = db.users

user_collection.delete_many({})

# adding a admin in user collection
exisiting_admin = user_collection.find_one({"user_id":admin_id})
if not exisiting_admin:
    user_collection.insert_one({
        "user_id":admin_id,
        "user_name":admin_name,
        "user_password":admin_password
    })

@user_app.route("/user")
class Get_User(MethodView):

    @user_app.response(200,User_Schema(many=True))
    def get(self):
        
        users = user_collection.find({"user_id":{"$ne":admin_id}})
        # present_users = users
        return users

@user_app.route("/create_user")
class Create_User(MethodView):

    @user_app.arguments(User_Create_Schema)
    @user_app.response(200,User_Schema)
    def post(self,data):

        #check if username already exists
        if user_collection.find_one({"user_name":data["user_name"]}):
            abort(400,message="Username already present.Please select other")
        

        #create an unique id for each user
        new_user_id = str(uuid.uuid4())

        #add the user id 
        data["user_id"] = new_user_id

        #hash the password and check if it satisfies the condition
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[`~!@#$%^&*_:|<>])[A-Za-z\d`~!@#$%^&*_:|<>]{4,}$"
        if not re.match(password_pattern,data["password"]):
            abort(400,message="Password should contain atleast one upper case, one lower case, one special character and one numerical character")

        password_hash = bcrypt.hashpw(data["password"].encode("utf-8"),bcrypt.gensalt())
        data["password"] = password_hash.decode("utf-8")

        try:
            result = user_collection.insert_one(data) 

        except Exception as e:
            print(f"Unable to create user: {e}")  

        new_user = user_collection.find_one({"_id":result.inserted_id})

        return new_user
