# Inventory Management System
A inventory management system designed for a wholesale business.
This application helps wholesalers manage bulk product orders, track stock levels, and streamline customer interactions.
- Users (buyers) can log in, browse products, and place bulk orders.
- Admins (wholesaler staff) can manage product catalogs, update quantities, monitor orders, and oversee user accounts.



## Features

## 1. User Management
- Secure admin profile with unique name and password.
- User authentication routes for login and account creation.
- Buyers must have an account to access inventory; otherwise, they can create one via the POST API in the user section.
- Only admins can view all registered buyers.
- Rate limiter added to prevent abuse when creating accounts.

## 2. Product Management
- Product catalog includes:
- id, name, type (enum), sku, timestamp, active (bool), quantity, price.
- Routes:
- POST → Add new products to the wholesaler’s catalog.
- GET → Retrieve all available products.
- Admins can update product details, adjust stock levels, and remove inactive products.

- Note: As of now only laptop is being used as product. Other products such as mobile, tv and refrigerator will be added soon.


## 3. Order Management
- GET → Retrieve all orders.
- POST → Buyers can place bulk orders by selecting product type, product, and quantity.
- PATCH → Cancel an order by providing user_id, order_id, and a valid reason.
- PATCH → Update product quantity (admin only).
- GET → Buyers can check their order status via user_order_status.
- PATCH (Admin only) → Admins can update order status (e.g., shipped, delivered).


## 4. Security & Access Control
- JWT authentication with role‑based access (admin vs buyer).
- Passwords stored securely using bcrypt hashing.
- Admin privileges:
- Manage products (CRUD).
- View and delete buyers.
- Update order statuses.


## 5. Testing
- Unit test cases added for user, product, and order routes.
- pytest and pytest-flask used for automated testing.


## 6. Tech Stack
- Backend: Flask 3.x
- Database: MongoDB Atlas (via PyMongo)
- Schemas: Marshmallow
- Authentication: Flask-JWT-Extended
- Rate Limiting: Flask-Limiter
- Environment Management: python-dotenv
- Testing: pytest, pytest-flask
- Deployment: Render (Gunicorn)

## 7. Deployment (Render)
- Push repo to GitHub.
- Create a new Web Service in Render.
- Connect your GitHub repo.
- Add environment variables in Render dashboard.
- Link: https://inventory-swagger.onrender.com/swagger-ui





