import os
from datetime import timedelta
from dotenv import load_dotenv,find_dotenv
from flask import Flask,config
from flask_jwt_extended import JWTManager
from routes.user_routes import *
from routes.product_routes import *   
from routes.order_routes import * 
from flask_smorest import Api

load_dotenv(find_dotenv())


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("SECRETKEY") #secret key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1) #token expires after 1 day 
app.config["API_SPEC_OPTIONS"] = {
    "security":[{"bearerAuth":[]}]
}
app.config["API_TITLE"]="Inventory"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/inventory"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

app.config["OPENAPI_SECURITY_SCHEMES"] = {
    "bearerAuth":{
        "type":"http",
        "scheme":"bearer",
        "bearerFormat":"JWT"
    }
}

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

api.register_blueprint(user_app)
api.register_blueprint(prouct_app)
api.register_blueprint(order_app)

if __name__=="__main__":
    app.run(debug=True)