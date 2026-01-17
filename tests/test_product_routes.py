import pytest
from unittest.mock import MagicMock
from datetime import datetime


class TestProductRoutes:
    """Test suite for product routes"""
    
    def test_get_products_as_admin(self, client, admin_token, mock_db, sample_product):
        """Test getting products as admin"""
        mock_db.products.find.return_value = [sample_product]
        
        response = client.get(
            '/product/get_products',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
    
    
    def test_get_products_as_user(self, client, user_token, mock_db, sample_product):
        """Test getting products as regular user (limited fields)"""
        mock_db.products.find.return_value = [sample_product]
        
        response = client.get(
            '/product/get_products',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
    
    
    def test_add_product_success(self, client, admin_token, mock_db):
        """Test adding product as admin"""
        mock_db.products.find_one.return_value = None
        mock_db.products.insert_one.return_value = MagicMock(inserted_id="mock_id")
        
        response = client.post(
            '/product/add_products',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                "product_type": "Laptop",
                "product_name": "MacBook Pro",
                "product_desc": "Apple laptop",
                "product_price": 2499.99,
                "quantity_present": 5,
                "is_active": True,
                "sku": "APPLE-MBP-001"
            }
        )
        
        assert response.status_code == 201
        assert 'product_id' in response.json
    
    
    def test_add_product_duplicate_sku(self, client, admin_token, mock_db, sample_product):
        """Test adding product with duplicate SKU"""
        mock_db.products.find_one.return_value = sample_product
        
        response = client.post(
            '/product/add_products',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                "product_type": "Laptop",
                "product_name": "MacBook Pro",
                "product_desc": "Apple laptop",
                "product_price": 2499.99,
                "quantity_present": 5,
                "is_active": True,
                "sku": "DELL-XPS-15-001"
            }
        )
        
        assert response.status_code == 409
    
    
    def test_add_product_unauthorized(self, client, user_token, mock_db):
        """Test adding product as regular user"""
        response = client.post(
            '/product/add_products',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "product_type": "Laptop",
                "product_name": "MacBook Pro",
                "product_desc": "Apple laptop",
                "product_price": 2499.99,
                "quantity_present": 5,
                "is_active": True,
                "sku": "APPLE-MBP-001"
            }
        )
        
        assert response.status_code == 403
    
    
    def test_update_product_success(self, client, admin_token, mock_db, sample_product):
        """Test updating product"""
        mock_db.products.find_one.return_value = sample_product
        
        response = client.put(
            '/product/update_product/prod-001',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                "product_name": "Dell XPS 15 Updated",
                "product_desc": "Updated description",
                "product_price": 1399.99,
                "quantity_present": 15,
                "is_active": True,
                "sku": "DELL-XPS-15-001"
            }
        )
        
        assert response.status_code == 200
    
    
    def test_update_product_not_found(self, client, admin_token, mock_db):
        """Test updating non-existent product"""
        mock_db.products.find_one.return_value = None
        
        response = client.put(
            '/product/update_product/nonexistent',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                "product_name": "Test Product",
                "product_desc": "Test description",
                "product_price": 99.99,
                "quantity_present": 10,
                "is_active": True,
                "sku": "TEST-001"
            }
        )
        
        assert response.status_code == 404
    
    
    def test_patch_product_price(self, client, admin_token, mock_db, sample_product):
        """Test partially updating product (price only)"""
        mock_db.products.find_one.return_value = sample_product
        
        response = client.patch(
            '/product/update/prod-001',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                "product_price": 1499.99
            }
        )
        
        assert response.status_code == 200
        assert 'old_price' in response.json
        assert 'new_price' in response.json
    
    
    def test_delete_product_success(self, client, admin_token, mock_db, sample_product):
        """Test deleting product"""
        mock_db.products.find_one.return_value = sample_product
        
        response = client.delete(
            '/product/delete_product/prod-001',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert 'message' in response.json
    
    
    def test_delete_product_not_found(self, client, admin_token, mock_db):
        """Test deleting non-existent product"""
        mock_db.products.find_one.return_value = None
        
        response = client.delete(
            '/product/delete_product/nonexistent',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 404
    
    
    def test_search_products(self, client, user_token, mock_db, sample_product):
        """Test searching products"""
        mock_db.products.find.return_value = [sample_product]
        
        response = client.get(
            '/product/search?q=Dell&type=Laptop',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)