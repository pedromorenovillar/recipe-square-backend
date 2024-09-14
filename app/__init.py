from flask import Flask
from flask_cors import CORS
from .db import init_db
from .routes import user_routes

def create_app():
    app = Flask(__name__)
    
    # Initializes CORS to connect to frontend || TODO change origins when frontend is deployed.
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8000", "http://127.0.0.1:8000"]}})
    
    # Initializes MongoDB
    init_db(app)
    
    # Registers blueprints or routes
    app.register_blueprint(user_routes, url_prefix='/api')

    return app