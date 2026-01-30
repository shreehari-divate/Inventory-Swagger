import os
from datetime import timedelta
from dotenv import load_dotenv,find_dotenv
from flask import Flask,config
from flask_jwt_extended import JWTManager
from routes.user_routes import user_app
from routes.product_routes import prouct_app   
from routes.order_routes import order_app
from flask_smorest import Api
from utils.rate_limiter import limiter
from config import config
from db.mongo_db import db
from utils.create_admin import admin_creation

load_dotenv(find_dotenv())


def create_app(config_name=None):


    app = Flask(__name__)

    # Load configuration
    env = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[env])


    api = Api(app)

    api.spec.components.security_scheme(
        "bearerAuth",{
            "type":"http",
            "scheme":"bearer",
            "bearerFormat":"JWT"
        }

    )

    api.security=[{"bearerAuth":[]}]
    jwt = JWTManager(app)
    limiter.init_app(app)

    with app.app_context():
        admin_creation(db)

    from routes.user_routes import user_app
    from routes.product_routes import prouct_app   
    from routes.order_routes import order_app
    api.register_blueprint(user_app)
    api.register_blueprint(prouct_app)
    api.register_blueprint(order_app)
    return app

app = create_app()

if __name__=="__main__":
    app.run()