from flask import Flask, session
from flask_session import Session
from flask_cors import CORS
from .db import init_db
from .routes import user_routes
from .config import Config

def create_app():
    app = Flask(__name__)

    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    
    # Initializes CORS to connect to frontend || TODO change origins when frontend is deployed.
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["http://localhost:8000"]}})
    
    # Initializes MongoDB
    init_db(app)
    
    # Registers blueprints or routes
    app.register_blueprint(user_routes, url_prefix='/api')

    # Imports config
    app.config.from_object(Config)

    return app