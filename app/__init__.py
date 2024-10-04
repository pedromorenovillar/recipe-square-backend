from flask import Flask, session
from flask_session import Session
from flask_cors import CORS
from .db import init_db
from .routes import user_routes, admin_routes, recipe_routes
from .config import Config
from flask_mail import Mail
from .mail import mail


def create_app():
    app = Flask(__name__)

    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    mail.init_app(app)
    Session(app)
    
    # Initializes CORS to connect to frontend || TO DO change origins when frontend is deployed.
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["http://localhost:8000"]}})
    

    # Initializes MongoDB
    init_db(app)
    
    # Registers blueprints or routes
    app.register_blueprint(user_routes, url_prefix='/api')
    app.register_blueprint(admin_routes, url_prefix='/api')
    app.register_blueprint(recipe_routes, url_prefix='/api')

    # Imports config
    app.config.from_object(Config)

    # Initializes Flask-Mail with the app
    mail.init_app(app)

    return app