import pytest
from unittest.mock import MagicMock
from datetime import datetime


class TestOrderRoutes:
    """Test suite for order routes"""
    
    def test_create_order_success(self, client, user_token, mock_db, sample_user, sample_product):
        """Test creating order successfully"""
        # Mock database responses
        mock_db.users.find_one.return_value = sample_user
        mock_db.products.find_one.return_value = sample_product
        mock_db.orders.insert_one.return_value = MagicMock(inserted_id="mock_id")
        
        response = client.post(
            '/orders/create_order',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "user_id": "user-001",
                "products": [
                    {
                        "sku": "DELL-XPS-15-001",
                        "product_name": "Dell XPS 15",
                        "product_type": "Laptop",
                        "product_quantity": 2
                    }
                ],
                "payment_method": "Credit Card",
                "shipping_address": "123 Test Street, Test City, 12345"
            }
        )
        
        assert response.status_code == 201
        assert 'order_details' in response.json
    
    
    def test_create_order_insufficient_stock(self, client, user_token, mock_db, sample_user, sample_product):
        """Test creating order with insufficient stock"""
        sample_product['quantity_present'] = 1
        mock_db.users.find_one.return_value = sample_user
        mock_db.products.find_one.return_value = sample_product
        
        response = client.post(
            '/orders/create_order',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "user_id": "user-001",
                "products": [
                    {
                        "sku": "DELL-XPS-15-001",
                        "product_name": "Dell XPS 15",
                        "product_type": "Laptop",
                        "product_quantity": 5
                    }
                ],
                "payment_method": "Credit Card",
                "shipping_address": "123 Test Street, Test City, 12345"
            }
        )
        
        assert response.status_code == 400
    
    
    def test_create_order_product_not_found(self, client, user_token, mock_db, sample_user):
        """Test creating order with non-existent product"""
        mock_db.users.find_one.return_value = sample_user
        mock_db.products.find_one.return_value = None
        
        response = client.post(
            '/orders/create_order',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "user_id": "user-001",
                "products": [
                    {
                        "sku": "NONEXISTENT-SKU",
                        "product_name": "Test Product",
                        "product_type": "Laptop",
                        "product_quantity": 1
                    }
                ],
                "payment_method": "Credit Card",
                "shipping_address": "123 Test Street, Test City, 12345"
            }
        )
        
        assert response.status_code == 404
    
    
    def test_create_order_inactive_product(self, client, user_token, mock_db, sample_user, sample_product):
        """Test creating order with inactive product"""
        sample_product['is_active'] = False
        mock_db.users.find_one.return_value = sample_user
        mock_db.products.find_one.return_value = sample_product
        
        response = client.post(
            '/orders/create_order',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "user_id": "user-001",
                "products": [
                    {
                        "sku": "DELL-XPS-15-001",
                        "product_name": "Dell XPS 15",
                        "product_type": "Laptop",
                        "product_quantity": 1
                    }
                ],
                "payment_method": "Credit Card",
                "shipping_address": "123 Test Street, Test City, 12345"
            }
        )
        
        assert response.status_code == 400
    
    
    def test_get_orders_admin(self, client, admin_token, mock_db, sample_order):
        """Test getting all orders as admin"""
        mock_db.orders.find.return_value = [sample_order]
        
        response = client.get(
            '/orders/get_orders',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
    
    
    def test_get_orders_unauthorized(self, client, user_token):
        """Test getting all orders as regular user"""
        response = client.get(
            '/orders/get_orders',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 403
    
    
    def test_get_my_orders(self, client, user_token, mock_db, sample_order):
        """Test getting user's own orders"""
        mock_db.orders.find.return_value = [sample_order]
        
        response = client.get(
            '/orders/my_orders',
            headers={'Authorization': f'Bearer {user_token}'}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
    
    
    def test_cancel_order_success(self, client, user_token, mock_db, sample_order):
        """Test cancelling order"""
        mock_db.orders.find_one.return_value = sample_order
        
        response = client.patch(
            '/orders/cancel_order/order-001',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "reason": "Changed my mind"
            }
        )
        
        assert response.status_code == 200
        assert 'message' in response.json
    
    
    def test_cancel_order_already_delivered(self, client, user_token, mock_db, sample_order):
        """Test cancelling delivered order"""
        sample_order['order_status'] = 'Delivered'
        mock_db.orders.find_one.return_value = sample_order
        
        response = client.patch(
            '/orders/cancel_order/order-001',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "reason": "Changed my mind"
            }
        )
        
        assert response.status_code == 400
    
    
    def test_cancel_order_not_found(self, client, user_token, mock_db):
        """Test cancelling non-existent order"""
        mock_db.orders.find_one.return_value = None
        
        response = client.patch(
            '/orders/cancel_order/nonexistent',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "reason": "Changed my mind"
            }
        )
        
        assert response.status_code == 404
    
    
    def test_update_order_quantity(self, client, user_token, mock_db, sample_order, sample_product):
        """Test updating product quantity in order"""
        mock_db.orders.find_one.side_effect = [sample_order, sample_order]
        mock_db.products.find_one.return_value = sample_product
        
        response = client.patch(
            '/orders/update_quantity/order-001/prod-001',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "product_quantity": 3
            }
        )
        
        assert response.status_code == 200
        assert 'order' in response.json
    
    
    def test_update_order_quantity_shipped(self, client, user_token, mock_db, sample_order):
        """Test updating quantity of shipped order"""
        sample_order['order_status'] = 'Shipped'
        mock_db.orders.find_one.return_value = sample_order
        
        response = client.patch(
            '/orders/update_quantity/order-001/prod-001',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "product_quantity": 3
            }
        )
        
        assert response.status_code == 403
    
    
    def test_update_shipping_address(self, client, user_token, mock_db, sample_order):
        """Test updating shipping address"""
        mock_db.orders.find_one.side_effect = [sample_order, sample_order]
        
        response = client.patch(
            '/orders/update_shipping_address/order-001',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "update_shipping_address": "456 New Address, New City, 54321"
            }
        )
        
        assert response.status_code == 200
        assert 'order' in response.json
    
    
    def test_update_shipping_address_delivered(self, client, user_token, mock_db, sample_order):
        """Test updating address of delivered order"""
        sample_order['order_status'] = 'Delivered'
        mock_db.orders.find_one.return_value = sample_order
        
        response = client.patch(
            '/orders/update_shipping_address/order-001',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "update_shipping_address": "456 New Address, New City, 54321"
            }
        )
        
        assert response.status_code == 403
    
    
    def test_update_order_status_admin(self, client, admin_token, mock_db, sample_order):
        """Test admin updating order status"""
        mock_db.orders.find_one.return_value = sample_order
        
        response = client.patch(
            '/orders/update_order_status/order-001',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                "order_status": "Shipped"
            }
        )
        
        assert response.status_code == 200
        assert 'new_status' in response.json
    
    
    def test_update_order_status_unauthorized(self, client, user_token, mock_db):
        """Test regular user trying to update order status"""
        response = client.patch(
            '/orders/update_order_status/order-001',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                "order_status": "Shipped"
            }
        )
        
        assert response.status_code == 403