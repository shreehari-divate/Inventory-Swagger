import bcrypt
from db.mongo_db import db
import os
from dotenv import load_dotenv,find_dotenv
from routes.user_routes import user_collection
load_dotenv

admin_name = os.getenv("ADMINNAME")
admin_password = os.getenv("ADMINPASSWORD")
admin_id = os.getenv("ADMINID")

admin = {
    "user_id": admin_id,
    "user_name": admin_name,
    "user_password": bcrypt.hashpw(admin_password.encode("utf-8"),bcrypt.gensalt()).decode("utf-8")
}
exisiting_admin = user_collection.find_one({"user_id":admin_id})
hashd_admin_pwd = bcrypt.hashpw(admin_password.encode("utf-8"),bcrypt.gensalt())
# if not exisiting_admin:
#     user_collection.insert_one({
#         "user_id":admin_id,
#         "user_name":admin_name,
#         "user_password":hashd_admin_pwd.decode("utf-8")
#     })
if not db.users.find_one({"user_name": admin["user_name"]}):
    db.users.insert_one(admin)
    print("Admin created")
else:
    print("Admin already exists")