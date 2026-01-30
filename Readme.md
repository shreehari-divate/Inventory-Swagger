# Inventory Management System
A full‑stack inventory management system designed for a wholesale business.
This application helps wholesalers manage bulk product orders, track stock levels, and streamline customer interactions.
- Users (buyers) can log in, browse products, and place bulk orders.
- Admins (wholesaler staff) can manage product catalogs, update quantities, monitor orders, and oversee user accounts.



## Features

## User Management
- Admin profile created with a unique name and password.
- User authentication routes for login and account creation.
- Users must have an account to access inventory; otherwise, they can create one via the POST API in the user section.
- Only admins can view all users.
- Rate limiter added to prevent abuse when creating users.
📦 Product Management
- Product collection includes:
- id, name, type (enum), sku, timestamp, active (bool), quantity, price.
- Routes:
- POST → Insert a product into the database.
- GET → Retrieve all products.
- Fixed user creation logic so only unauthorized users can create new accounts.

🛒 Order Management
- GET → Retrieve orders.
- POST → Create an order for the current user with a list of products.
- PATCH → Cancel an order by providing user_id, order_id, and a valid reason.
- PATCH → Update product quantity.
- GET → Check order status via user_order_status API.
- PATCH (Admin only) → Update order status.

🛡️ Security & Access Control
- JWT authentication with role‑based access (admin vs user).
- Admin privileges:
- Manage products (CRUD).
- View all users.
- Delete users.
- Update order status.
- Passwords stored securely using bcrypt hashing.

🧪 Testing
- Unit test cases added for user, product, and order routes.
- pytest and pytest-flask used for automated testing.

📖 Documentation
- Enhanced Swagger/OpenAPI documentation:
- Detailed descriptions.
- Example payloads for clarity.

⚡ Rate Limiting
- Implemented using Flask-Limiter.
- Default limits: 200 requests/day, 50 requests/hour.
- Helps prevent abuse of user creation and other sensitive endpoints.

🛠️ Tech Stack
- Backend: Flask 3.x
- Database: MongoDB Atlas (via PyMongo)
- Schemas: Marshmallow
- Authentication: Flask-JWT-Extended
- Rate Limiting: Flask-Limiter
- Environment Management: python-dotenv
- Testing: pytest, pytest-flask
- Deployment: Render (Gunicorn)

🚀 Deployment (Render)
- Push repo to GitHub.
- Create a new Web Service in Render.
- Connect your GitHub repo.
- Add environment variables from .env.example in Render dashboard.
- Render will:
- Install dependencies from requirements.txt.
- Start app using Procfile:
web: gunicorn app:app




