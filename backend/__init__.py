from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS

# CRM_SERVICE_URL = "http://127.0.0.1:8000/integrate/ticket"
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/ssd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

CORS(app, supports_credentials=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)


from backend.routes.auth import auth_bp
from backend.routes.ticket import ticket_bp
from backend.routes.dashboard import dash_bp
from backend.routes.customer import cust_bp

app.register_blueprint(auth_bp)
app.register_blueprint(ticket_bp)
app.register_blueprint(dash_bp)
app.register_blueprint(cust_bp)