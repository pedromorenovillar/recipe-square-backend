from flask import Blueprint, request, jsonify
from .db import get_db
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.security import generate_password_hash, check_password_hash

user_routes = Blueprint('user_routes', __name__)

# API endpoint 1: registering a user in the DB
@user_routes.route('/register', methods=['POST'])
def register_user():
  try:
    # Log the incoming JSON data from the frontend
    user_data = request.get_json()
    hashed_password = generate_password_hash(user_data['password'], method='sha256')

    db = get_db()
    users = db.users

    # Insert the user into MongoDB
    new_user = {
        "username": user_data["username"],
        "email": user_data["email"],
        "password": hashed_password
    }

    result = users.insert_one(new_user)
    print(f"Inserted user with _id: {result.inserted_id}")

    return jsonify({f"message": "User registered successfully", "id": str(result.inserted_id)}), 201
  
  except DuplicateKeyError:
    return jsonify({"error": "Username or Email already exists"}), 400

  except PyMongoError as e:
    print(f"Error registering user into MongoDB: {e}")
    return jsonify({"error": "Database registration failed"}), 500

  except Exception as e:
    print(f"Unexpected error: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500
  
# API endpoint 2: login a user in the DB
# API endpoint 3: updating a user in the DB
# API endpoint 4: deleting a user in the DB

# API endpoint 5: adding a recipe in the DB
# API endpoint 6: updating a recipe in the DB
# API endpoint 7: deleting a recipe in the DB

# API endpoint 8: adding a comment in the DB
# API endpoint 9: updating a comment in the DB
# API endpoint 10: deleting a comment in the DB