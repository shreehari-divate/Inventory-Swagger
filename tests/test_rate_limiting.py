import pytest
from unittest.mock import MagicMock, patch
from bson import ObjectId
import bcrypt
import os
import sys
import importlib


class TestRateLimiting:
    """Test suite for rate limiting"""
    
    def test_create_user_rate_limit(self, mock_db):
        """Test that create user endpoint is rate limited (2 per hour)"""
        # Save and clear modules to force reimport
        saved_modules = {}
        modules_to_clear = ['app', 'utils.rate_limiter', 'routes.user_routes', 
                           'routes.product_routes', 'routes.order_routes']
        
        for mod in modules_to_clear:
            if mod in sys.modules:
                saved_modules[mod] = sys.modules[mod]
                del sys.modules[mod]
        
        # Temporarily disable testing mode to enable rate limiting
        old_testing = os.environ.get('TESTING')
        os.environ['TESTING'] = 'False'
        
        try:
            # Import fresh app with rate limiting enabled
            with patch('db.mongo_db.db', mock_db):
                with patch('routes.user_routes.user_collection', mock_db.users):
                    with patch('routes.product_routes.product_collection', mock_db.products):
                        with patch('routes.order_routes.order_collection', mock_db.orders):
                            with patch('routes.order_routes.user_collection', mock_db.users):
                                with patch('routes.order_routes.product_collection', mock_db.products):
                                    from app import create_app
                                    app = create_app()
                                    app.config['TESTING'] = True
                                    client = app.test_client()
            
            mock_db.users.reset_mock()
            
            # Mock successful user creation
            new_user = {
                "_id": ObjectId(),
                "user_id": "new-user-001",
                "user_name": "newuser",
                "user_role": "user"
            }
            
            mock_db.users.insert_one.return_value = MagicMock(inserted_id=new_user["_id"])
            
            # Make 2 successful requests (at the limit)
            for i in range(2):
                # Reset side_effect for each iteration
                mock_db.users.find_one.side_effect = [None, {**new_user, "user_name": f"newuser{i}"}]
                
                response = client.post(
                    '/user/create_user',
                    json={
                        "user_name": f"newuser{i}",
                        "user_password": "Test@123"
                    }
                )
                assert response.status_code == 200
            
            # 3rd request should be rate limited
            response = client.post(
                '/user/create_user',
                json={
                    "user_name": "newuser3",
                    "user_password": "Test@123"
                }
            )
            assert response.status_code == 429  # Too Many Requests
        
        finally:
            # Restore testing mode
            if old_testing:
                os.environ['TESTING'] = old_testing
            else:
                os.environ['TESTING'] = 'True'  # Set back to True for other tests
            
            # Restore modules
            for mod in modules_to_clear:
                if mod in sys.modules:
                    del sys.modules[mod]
            for mod, module in saved_modules.items():
                sys.modules[mod] = module
    
    
    def test_login_rate_limit(self, sample_user, mock_db):
        """Test that login endpoint is rate limited (10 per hour)"""
        # Save and clear modules to force reimport
        saved_modules = {}
        modules_to_clear = ['app', 'utils.rate_limiter', 'routes.user_routes', 
                           'routes.product_routes', 'routes.order_routes']
        
        for mod in modules_to_clear:
            if mod in sys.modules:
                saved_modules[mod] = sys.modules[mod]
                del sys.modules[mod]
        
        # Temporarily disable testing mode to enable rate limiting
        old_testing = os.environ.get('TESTING')
        os.environ['TESTING'] = 'False'
        
        try:
            # Import fresh app with rate limiting enabled
            with patch('db.mongo_db.db', mock_db):
                with patch('routes.user_routes.user_collection', mock_db.users):
                    with patch('routes.product_routes.product_collection', mock_db.products):
                        with patch('routes.order_routes.order_collection', mock_db.orders):
                            with patch('routes.order_routes.user_collection', mock_db.users):
                                with patch('routes.order_routes.product_collection', mock_db.products):
                                    from app import create_app
                                    app = create_app()
                                    app.config['TESTING'] = True
                                    client = app.test_client()
            
            mock_db.users.reset_mock()
            # Use return_value instead of side_effect to avoid exhaustion
            mock_db.users.find_one.return_value = sample_user
            
            # Make 10 successful requests (at the limit)
            for i in range(10):
                response = client.post(
                    '/user/generate_token/testuser',
                    json={
                        "user_password": "Test@123"
                    }
                )
                assert response.status_code == 200, f"Request {i+1} failed: {response.get_json()}"
            
            # 11th request should be rate limited
            response = client.post(
                '/user/generate_token/testuser',
                json={
                    "user_password": "Test@123"
                }
            )
            assert response.status_code == 429  # Too Many Requests
        
        finally:
            # Restore testing mode
            if old_testing:
                os.environ['TESTING'] = old_testing
            else:
                os.environ['TESTING'] = 'True'
            
            # Restore modules
            for mod in modules_to_clear:
                if mod in sys.modules:
                    del sys.modules[mod]
            for mod, module in saved_modules.items():
                sys.modules[mod] = module
    
    
    def test_reset_password_rate_limit(self, mock_db):
        """Test that reset password endpoint is rate limited (3 per hour)"""
        # Save and clear modules to force reimport
        saved_modules = {}
        modules_to_clear = ['app', 'utils.rate_limiter', 'routes.user_routes', 
                           'routes.product_routes', 'routes.order_routes']
        
        for mod in modules_to_clear:
            if mod in sys.modules:
                saved_modules[mod] = sys.modules[mod]
                del sys.modules[mod]
        
        # Temporarily disable testing mode to enable rate limiting
        old_testing = os.environ.get('TESTING')
        os.environ['TESTING'] = 'False'
        
        try:
            # Import fresh app with rate limiting enabled
            with patch('db.mongo_db.db', mock_db):
                with patch('routes.user_routes.user_collection', mock_db.users):
                    with patch('routes.product_routes.product_collection', mock_db.products):
                        with patch('routes.order_routes.order_collection', mock_db.orders):
                            with patch('routes.order_routes.user_collection', mock_db.users):
                                with patch('routes.order_routes.product_collection', mock_db.products):
                                    from app import create_app
                                    app = create_app()
                                    app.config['TESTING'] = True
                                    client = app.test_client()
            
            # Create token first
            hashed_password = bcrypt.hashpw("Test@123".encode("utf-8"), bcrypt.gensalt())
            test_user = {
                "_id": ObjectId(),
                "user_id": "user-001",
                "user_name": "testuser",
                "user_password": hashed_password.decode("utf-8"),
                "user_role": "user"
            }
            
            # Use return_value for token generation
            mock_db.users.find_one.return_value = test_user
            
            # Get token
            response = client.post(
                '/user/generate_token/testuser',
                json={"user_password": "Test@123"}
            )
            assert response.status_code == 200
            token = response.get_json()['token']
            
            mock_db.users.reset_mock()
            # Use return_value to avoid exhaustion
            mock_db.users.find_one.return_value = test_user
            mock_db.users.update_one.return_value = MagicMock()
            
            # Make 3 successful requests (at the limit)
            for i in range(3):
                response = client.patch(
                    '/user/reset_password/testuser',
                    headers={'Authorization': f'Bearer {token}'},
                    json={
                        "user_password": "Test@123",
                        "new_password": f"NewTest@12{i}"
                    }
                )
                assert response.status_code == 201, f"Request {i+1} failed: {response.get_json()}"
            
            # 4th request should be rate limited
            response = client.patch(
                '/user/reset_password/testuser',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    "user_password": "Test@123",
                    "new_password": "NewTest@124"
                }
            )
            assert response.status_code == 429  # Too Many Requests
        
        finally:
            # Restore testing mode
            if old_testing:
                os.environ['TESTING'] = old_testing
            else:
                os.environ['TESTING'] = 'True'
            
            # Restore modules
            for mod in modules_to_clear:
                if mod in sys.modules:
                    del sys.modules[mod]
            for mod, module in saved_modules.items():
                sys.modules[mod] = module
    
    
    def test_rate_limit_disabled_in_normal_tests(self, client, mock_db):
        """Test that rate limiting is disabled by default in tests"""
        # Verify testing mode is enabled
        assert os.environ.get('TESTING') == 'True', "TESTING should be True for normal tests"
        
        mock_db.users.reset_mock()
        
        # Set up mock to work for multiple iterations
        new_user = {
            "_id": ObjectId(),
            "user_id": "new-user-001",
            "user_name": "newuser",
            "user_role": "user"
        }
        
        mock_db.users.insert_one.return_value = MagicMock(inserted_id=new_user["_id"])
        
        # Should be able to make many requests without hitting rate limit
        for i in range(10):
            # Reset side_effect for each iteration
            mock_db.users.find_one.side_effect = [None, {**new_user, "user_name": f"newuser{i}"}]
            
            response = client.post(
                '/user/create_user',
                json={
                    "user_name": f"newuser{i}",
                    "user_password": "Test@123"
                }
            )
            # If this fails, rate limiting is not actually disabled
            if response.status_code != 200:
                print(f"Failed on iteration {i}: {response.status_code} - {response.get_json()}")
            assert response.status_code == 200, f"Rate limiting should be disabled in tests, got {response.status_code}"