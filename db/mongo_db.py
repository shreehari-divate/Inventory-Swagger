from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
# client = MongoClient("mongodb://localhost:27017")
# db = client["user_db"]

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
import logging

class Database:
    _instance = None
    _client = None
    _db = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        if self._client is None:
            try:
                # mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
                mongo_uri = os.getenv('MONGO_URI')
                print(f"Connecting to MongoDB at: {mongo_uri}")
                self._client = MongoClient(
                    mongo_uri,
                    maxPoolSize=50,
                    minPoolSize=10,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    retryWrites=True
                )
                # Test connection
                self._client.admin.command('ping')
                logging.info("MongoDB connected successfully")
            except ConnectionFailure as e:
                logging.error(f"MongoDB connection failed: {e}")
                raise
        return self._client
    
    def get_database(self, db_name=None):
       if db_name is None:
            # Use your actual database name as default
            db_name = os.getenv('MONGO_DB_NAME', 'user_db')
            print(f"Using database name: {db_name}")
        
       client = self.connect()
       self._db = client[db_name]
        
    #    logger.info(f"Using database: {db_name}")
       return self._db

db_instance = Database()
db = db_instance.get_database()