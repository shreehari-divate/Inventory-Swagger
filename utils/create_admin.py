import bcrypt
from db.mongo_db import db
import os
from dotenv import load_dotenv,find_dotenv
from pymongo import MongoClient
# from routes.user_routes import user_collection
load_dotenv(find_dotenv())

admin_name = os.getenv("ADMINNAME")
admin_password = os.getenv("ADMINPASSWORD")
admin_id = os.getenv("ADMINID")
# mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
# mongo_db_name = os.getenv('MONGO_DB_NAME', 'user_db')


def admin_creation(db):
    # client = MongoClient(mongo_uri)
    # db = client[mongo_db_name]
    # user_collection = db.users
    
    admin_name = os.getenv("ADMINNAME")
    admin_password = os.getenv("ADMINPASSWORD")
    admin_id = os.getenv("ADMINID")

    #check for exsiting admin
    existing_admin = db.users.find_one({"user_name": admin_name})
    
    if existing_admin:
        print(f"Admin user '{admin_name}' already exists")
        return existing_admin
    
    hashed_password = bcrypt.hashpw(
        admin_password.encode("utf-8"), 
        bcrypt.gensalt()
    )
    db.users.insert_one({
        "user_id": admin_id,
        "user_name": admin_name,
        "user_password": hashed_password.decode("utf-8"),
        "user_role": "admin"
    })
    print("Admin created successfully")
    
    return db.users.find_one({"user_name": admin_name})
