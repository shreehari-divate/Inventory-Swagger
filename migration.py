from pymongo import MongoClient

# connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["user_db"]

# collections
user_collection = db.users
order_collection = db.orders

# Step 1: find all order documents in users collection
orders = list(user_collection.find({"order_id": {"$exists": True}}))

print(f"Found {len(orders)} order documents to migrate.")

# Step 2: insert them into orders collection
if orders:
    order_collection.insert_many(orders)
    print("Orders inserted into 'orders' collection.")

    # Step 3: remove them from users collection
    user_collection.delete_many({"order_id": {"$exists": True}})
    print("Orders removed from 'users' collection.")