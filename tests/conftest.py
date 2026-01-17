import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime
import bcrypt
from bson import ObjectId

# Add parent directory to Python path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

# Set environment variables BEFORE importing app
os.environ['SECRETKEY'] = 'test-secret-key'
os.environ['ADMINNAME'] = 'admin'
os.environ['ADMINPASSWORD'] = 'Admin@123'
os.environ['ADMINID'] = 'admin-001'


@pytest.fixture
def mock_db():
    """Mock MongoDB database and collections"""
    mock_database = MagicMock()
    mock_database.users = MagicMock()
    mock_database.products = MagicMock()
    mock_database.orders = MagicMock()
    return mock_database


@pytest.fixture
def app(mock_db):
    """Create and configure test Flask application"""
    # Patch before importing
    with patch('db.mongo_db.db', mock_db):
        with patch('routes.user_routes.user_collection', mock_db.users):
            with patch('routes.product_routes.product_collection', mock_db.products):
                with patch('routes.order_routes.order_collection', mock_db.orders):
                    with patch('routes.order_routes.user_collection', mock_db.users):
                        with patch('routes.order_routes.product_collection', mock_db.products):
                            from app import create_app
                            
                            app = create_app()
                            app.config['TESTING'] = True
                            app.config['JWT_SECRET_KEY'] = 'test-secret-key'
                            
                            yield app


@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture
def sample_user():
    """Sample user data"""
    hashed_password = bcrypt.hashpw("Test@123".encode("utf-8"), bcrypt.gensalt())
    return {
        "_id": ObjectId(),  # Add MongoDB _id
        "user_id": "user-001",
        "user_name": "testuser",
        "user_password": hashed_password.decode("utf-8"),
        "user_role": "user"
    }


@pytest.fixture
def sample_admin():
    """Sample admin data"""
    hashed_password = bcrypt.hashpw("Admin@123".encode("utf-8"), bcrypt.gensalt())
    return {
        "_id": ObjectId(),  # Add MongoDB _id
        "user_id": "admin-001",
        "user_name": "admin",
        "user_password": hashed_password.decode("utf-8"),
        "user_role": "admin"
    }


@pytest.fixture
def sample_product():
    """Sample product data"""
    return {
        "_id": ObjectId(),  # Add MongoDB _id
        "product_id": "prod-001",
        "product_type": "Laptop",
        "product_name": "Dell XPS 15",
        "product_desc": "High performance laptop",
        "product_price": 1299.99,
        "quantity_present": 10,
        "is_active": True,
        "sku": "DELL-XPS-15-001",
        "timestamp": datetime.now()
    }


@pytest.fixture
def sample_order(sample_user, sample_product):
    """Sample order data"""
    return {
        "_id": ObjectId(),  # Add MongoDB _id
        "order_id": "order-001",
        "user_name": sample_user["user_name"],
        "user_id": sample_user["user_id"],
        "products": [
            {
                "product_id": sample_product["product_id"],
                "sku": sample_product["sku"],
                "product_name": sample_product["product_name"],
                "product_type": sample_product["product_type"],
                "product_price": sample_product["product_price"],
                "product_quantity": 2,
                "total_price": sample_product["product_price"] * 2
            }
        ],
        "order_quantity": 2,
        "order_price": sample_product["product_price"] * 2,
        "order_status": "Pending",
        "payment_status": "Pending",
        "payment_method": "Credit Card",
        "shipping_address": "123 Test Street, Test City, 12345",
        "created_at": datetime.now()
    }


@pytest.fixture
def user_token(client, sample_user, mock_db):
    """Generate JWT token for regular user"""
    mock_db.users.find_one.return_value = sample_user
    
    response = client.post(
        '/user/generate_token/testuser',
        json={
            "user_password": "Test@123"
        }
    )
    
    if response.status_code == 200:
        data = response.get_json()
        return data.get('token')
    return None


@pytest.fixture
def admin_token(client, sample_admin, mock_db):
    """Generate JWT token for admin"""
    mock_db.users.find_one.return_value = sample_admin
    
    response = client.post(
        '/user/generate_token/admin',
        json={
            "user_password": "Admin@123"
        }
    )
    
    if response.status_code == 200:
        data = response.get_json()
        return data.get('token')
    return None