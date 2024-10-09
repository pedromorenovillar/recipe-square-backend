from flask import Flask, session
from flask_session import Session
from flask_cors import CORS
from .db import init_db
from .routes import user_routes, admin_routes, recipe_routes
from .config import Config
from flask_mail import Mail
from .mail import mail
import logging
import os


def create_app():
    app = Flask(__name__)

    # Imports config before accessing app.config
    app.config.from_object(Config)  # Load configuration from Config class

    logging.info(f"ENV: {app.config['ENV']}")
    logging.info(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")

    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    mail.init_app(app)
    Session(app)
    
    # CORS configuration
    if app.config['ENV'] == 'production':
        # Allows requests from the deployed frontend in production
        CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["https://recipe-square-frontend-5c021339c6db.herokuapp.com"]}})
    else:
        # Allows requests from localhost in development
        CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["http://localhost:5173"]}})
    

    # Initializes MongoDB
    init_db(app)
    
    # Registers blueprints or routes
    app.register_blueprint(user_routes, url_prefix='/api')
    app.register_blueprint(admin_routes, url_prefix='/api')
    app.register_blueprint(recipe_routes, url_prefix='/api')

    # Initializes Flask-Mail with the app
    mail.init_app(app)

    return app