import uuid
import re
import bcrypt
from db import db
from flask_smorest import Blueprint,abort
from flask.views import MethodView
from schema.user_schema import User_Schema,User_Create_Schema, User_reset_password,Token_Schema
from db.mongo_db import db
import os
from dotenv import load_dotenv,find_dotenv
from flask_jwt_extended import create_access_token,jwt_required,get_jwt


load_dotenv(find_dotenv())

admin_name = os.getenv("ADMINNAME")
admin_password = os.getenv("ADMINPASSWORD")
admin_id = os.getenv("ADMINID")
user_app = Blueprint("user","__name__",url_prefix="/user")

#user collection
user_collection = db.users

# user_collection.delete_many({})

# adding a admin in user collection
exisiting_admin = user_collection.find_one({"user_id":admin_id})
hashd_admin_pwd = bcrypt.hashpw(admin_password.encode("utf-8"),bcrypt.gensalt())
if not exisiting_admin:
    user_collection.insert_one({
        "user_id":admin_id,
        "user_name":admin_name,
        "user_password":hashd_admin_pwd.decode("utf-8")
    })


'''
Get User (Admin Only)
'''    

@user_app.route("/get_user")
class Get_User(MethodView):

    @jwt_required()
    @user_app.response(200,User_Schema(many=True))
    def get(self):
        claims = get_jwt()

        if claims.get("role")!="admin":
            abort(403,message="Admins Only")
        
        users = list(user_collection.find({"user_id":{"$ne":admin_id}}))
        # present_users = users
        return users

'''
Create User
'''

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
        if not re.match(password_pattern,data["user_password"]):
            abort(400,message="Password should contain atleast one upper case, one lower case, one special character and one numerical character")

        password_hash = bcrypt.hashpw(data["user_password"].encode("utf-8"),bcrypt.gensalt())
        data["user_password"] = password_hash.decode("utf-8")

        try:
            result = user_collection.insert_one(data) 

        except Exception as e:
            print(f"Unable to create user: {e}")  
            abort(500,message="Unable to create User")

        new_user = user_collection.find_one({"_id":result.inserted_id})

        return new_user
    

@user_app.route("/reset_password/<user_name>")
class Reset_User_Password(MethodView):

    @user_app.arguments(User_reset_password)
    @user_app.response(201)
    def patch(self,data,user_name):

        user = user_collection.find_one({"user_name":user_name})

        if not user:
            abort(404,message="No such username present")

        if not bcrypt.checkpw(data["user_password"].encode("utf-8"), user["user_password"].encode("utf-8")):
            abort(400,message="Bad Request,password does not match")   

        updated_password = bcrypt.hashpw(data["new_password"].encode("utf-8"),bcrypt.gensalt()).decode("utf-8") 
        user_collection.update_one(
            {
                "user_name":user_name
            },
            {
                "$set":{
                    "user_password":updated_password
                }
            }
        )   

        return "Password updated successfully"
    
@user_app.route("/generate_token/<user_name>")
class Create_Access_Token(MethodView):
    
    @user_app.arguments(Token_Schema)
    def post(self,data,user_name):
        
        user = user_collection.find_one({"user_name":user_name})

        if not user:
            abort(404,message="User not found")

        if not bcrypt.checkpw(data["user_password"].encode("utf-8"),user["user_password"].encode("utf-8")):
            abort(400,message="Bad request, password does not match")    

        token = create_access_token(identity=str(user["_id"]),
                                    additional_claims={"role":"admin" if user["user_name"]==admin_name else "user"}
                                    )

        return {"id":str(user["_id"]),"user":user_name,"token":token}                    