import pytest
from unittest.mock import MagicMock
import bcrypt
from bson import ObjectId


class TestUserRoutes:
    """Test suite for user routes"""
    
    def test_create_user_success(self, client, mock_db):
        """Test successful user creation"""
        # Reset mock
        mock_db.users.reset_mock()
        
        # Mock that username doesn't exist, then return the new user
        new_user = {
            "_id": ObjectId(),
            "user_id": "new-user-001",
            "user_name": "newuser",
            "user_role": "user"
        }
        
        # First call returns None (username doesn't exist)
        # Second call returns the new user (after insert)
        mock_db.users.find_one.side_effect = [None, new_user]
        mock_db.users.insert_one.return_value = MagicMock(inserted_id=new_user["_id"])
        
        response = client.post(
            '/user/create_user',
            json={
                "user_name": "newuser",
                "user_password": "Test@123"
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user_name'] == "newuser"
        assert 'user_password' not in data
    
    
    def test_create_user_weak_password(self, client, mock_db):
        """Test user creation with weak password"""
        mock_db.users.reset_mock()
        
        response = client.post(
            '/user/create_user',
            json={
                "user_name": "newuser",
                "user_password": "weak"
            }
        )
        
        assert response.status_code == 400
    
    
    def test_create_user_duplicate_username(self, client, mock_db):
        """Test user creation with existing username"""
        mock_db.users.reset_mock()
        mock_db.users.find_one.return_value = {
            "_id": ObjectId(),
            "user_name": "existinguser"
        }
        
        response = client.post(
            '/user/create_user',
            json={
                "user_name": "existinguser",
                "user_password": "Test@123"
            }
        )
        
        assert response.status_code == 400
    
    
    def test_login_success(self, client, sample_user, mock_db):
        """Test successful login"""
        mock_db.users.reset_mock()
        mock_db.users.find_one.return_value = sample_user
        
        response = client.post(
            '/user/generate_token/testuser',
            json={
                "user_password": "Test@123"
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert data['user'] == "testuser"
    
    
    def test_login_invalid_credentials(self, client, sample_user, mock_db):
        """Test login with invalid password"""
        mock_db.users.reset_mock()
        mock_db.users.find_one.return_value = sample_user
        
        response = client.post(
            '/user/generate_token/testuser',
            json={
                "user_password": "WrongPassword@123"
            }
        )
        
        assert response.status_code == 401
    
    
    def test_login_nonexistent_user(self, client, mock_db):
        """Test login with non-existent user"""
        mock_db.users.reset_mock()
        mock_db.users.find_one.return_value = None
        
        response = client.post(
            '/user/generate_token/nonexistent',
            json={
                "user_password": "Test@123"
            }
        )
        
        assert response.status_code == 404
    
    
    def test_get_users_admin(self, client, admin_token, mock_db):
        """Test getting all users as admin"""
        mock_db.users.reset_mock()
        users = [
            {"user_id": "user-001", "user_name": "user1"},
            {"user_id": "user-002", "user_name": "user2"}
        ]
        
        # Mock find to return list (not iterator)
        mock_db.users.find.return_value = users
        
        response = client.get(
            '/user/get_user',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2
    
    
    def test_get_users_unauthorized(self, client, user_token):
        """Test getting all users as regular user"""
        response = client.get(
            '/user/get_user',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 403
    
    
    def test_reset_password_success(self, client, user_token,mock_db):
        """Test successful password reset"""
        mock_db.users.reset_mock()
        
        # Create user with known password hash
        hashed_password = bcrypt.hashpw("Test@123".encode("utf-8"), bcrypt.gensalt())
        test_user = {
            "_id": ObjectId(),
            "user_id": "user-001",
            "user_name": "testuser",
            "user_password": hashed_password.decode("utf-8"),
            "user_role": "user"
        }
        
        # Set return value (not side_effect)
        mock_db.users.find_one.return_value = test_user
        mock_db.users.find_one.side_effect = None  # Clear any side_effect
        mock_db.users.update_one.return_value = MagicMock()
        
        response = client.patch(
            '/user/reset_password/testuser',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "user_password": "Test@123",
                "new_password": "NewTest@123"
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == "Password updated successfully"
    
    
    def test_reset_password_wrong_current(self, client, user_token,mock_db):
        """Test password reset with wrong current password"""
        mock_db.users.reset_mock()
        
        # Create user with known password hash
        hashed_password = bcrypt.hashpw("Test@123".encode("utf-8"), bcrypt.gensalt())
        test_user = {
            "_id": ObjectId(),
            "user_id": "user-001",
            "user_name": "testuser",
            "user_password": hashed_password.decode("utf-8"),
            "user_role": "user"
        }
        
        mock_db.users.find_one.return_value = test_user
        mock_db.users.find_one.side_effect = None  # Clear any side_effect
        
        response = client.patch(
            '/user/reset_password/testuser',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "user_password": "WrongPassword@123",
                "new_password": "NewTest@123"
            }
        )
        
        assert response.status_code == 401
    
    
    def test_reset_password_user_not_found(self, client,user_token, mock_db):
        """Test password reset for non-existent user"""
        mock_db.users.reset_mock()
        mock_db.users.find_one.return_value = None
        mock_db.users.find_one.side_effect = None  # Clear any side_effect
        
        response = client.patch(
            '/user/reset_password/nonexistent',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "user_password": "Test@123",
                "new_password": "NewTest@123"
            }
        )
        
        assert response.status_code == 404
    
    
    def test_create_user_already_logged_in(self, client, user_token, mock_db):
        """Test that logged-in users cannot create new accounts"""
        response = client.post(
            '/user/create_user',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "user_name": "newuser",
                "user_password": "Test@123"
            }
        )
        
        assert response.status_code == 403