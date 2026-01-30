# config.py
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRETKEY')
    # JWT_SECRET_KEY = os.getenv('SECRETKEY')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

    # API Documentation Configuration
    API_SPEC_OPTIONS = {
        "security": [{"bearerAuth": []}]
    }
    API_TITLE = "Inventory"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/inventory"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    OPENAPI_SECURITY_SCHEMES = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'user_db')
    
    # Admin Configuration
    ADMIN_NAME = os.getenv("ADMINNAME", "admin") #admin is default username
    ADMIN_PASSWORD = os.getenv("ADMINPASSWORD", "Admin@123") #Admin@123 is default password
    ADMIN_ID = os.getenv("ADMINID", "admin-001") #admin-001 is default admin id
    
    # Rate Limiting
    RATELIMIT_STORAGE_URI = "memory://"
    
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    MONGO_URI = 'mongodb://localhost:27017/'
    MONGO_DB_NAME = 'user_db'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    MONGO_URI = os.getenv('MONGO_URI')  # Required in production
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'user_db')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # Shorter for production
    # RATELIMIT_STORAGE_URI = os.getenv('RATELIMIT_STORAGE_URI', 'redis://localhost:6379/0')

    
class TestingConfig(Config):
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017'
    MONGO_DB_NAME = 'user_db_test'
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}