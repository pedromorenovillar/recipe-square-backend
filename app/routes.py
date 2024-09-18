from flask import Blueprint, request, jsonify, session
from functools import wraps
from .db import get_db
from pymongo.errors import PyMongoError
import bcrypt

user_routes = Blueprint('user_routes', __name__)

# API endpoint 1: registering a user in the DB
@user_routes.route('/register_user', methods=['POST'])
def register_user():
  try:
    # Log the incoming JSON data from the frontend || TODO remove print log
    user_data = request.get_json()
    print("Received data:", user_data)
    hashed_password = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())

    user_data["username"] = user_data["username"].lower()
    user_data["email"] = user_data["email"].lower()

    # Get users collection from DB
    db = get_db()
    users = db.users

    # Check if the username or email already exists in the database || TODO remove print log
    existing_user = users.find_one({"$or": [{"username": user_data["username"]}, {"email": user_data["email"]}]})
    print(f"Existing user found: {existing_user}")
    
    if existing_user:
      return jsonify({"error": "Username or email already exists"}), 400

    # Insert the user into MongoDB users collection
    new_user = {
        "username": user_data["username"],
        "email": user_data["email"],
        "password": hashed_password
    }

    result = users.insert_one(new_user)
    # TODO remove logs
    print(f"Inserted user with _id: {result.inserted_id}")

    return jsonify({f"message": "User registered successfully", "id": str(result.inserted_id)}), 201
  
  except PyMongoError as e:
    print(f"Error registering user into MongoDB: {e}")
    return jsonify({"error": "Database registration failed"}), 500

  except Exception as e:
    print(f"Unexpected error: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500
  
# API endpoint 2: login a user in the DB
@user_routes.route('/login_user', methods=['POST'])
def login_user():
  try:
    login_data = request.get_json()
    username = login_data.get("username").lower()
    password = login_data.get("password").lower()
    email = login_data.get("email").lower()

    print("Received data:", login_data) # TO DO: remove log

    db = get_db()
    users = db.users

    user = users.find_one({"$or": [{"username": username}, {"email": email}]})

    if not user:
      return jsonify({"error": "User not found"}), 404

    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
      session['user_id'] = str(user['_id'])
      session['username'] = user['username']
      print("Session data after login:", dict(session))

      return jsonify({"message": "Login successful"}), 200
    else:
      return jsonify({"error": "Invalid password"}), 400

  except Exception as e:
    print(f"Error during login: {e}")
    return jsonify({"error": "An error occurred during login"}), 500

# Decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Check if user is logged in
@user_routes.route('/check_session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({"logged_in": True}), 200
    else:
        return jsonify({"logged_in": False}), 200

# Log user out
@user_routes.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clears session data
    response = jsonify({"message": "Logged out successfully"})

    # Expire the session cookie
    response.set_cookie('session', '', expires=0, samesite='Lax', secure=False)

    return response


# API endpoint 5: updating a user in the DB
# API endpoint 6: deleting a user in the DB

# API endpoint 7: adding a recipe in the DB


# API endpoint 8: adding a comment in the DB
# API endpoint 9: updating a comment in the DB
# API endpoint 10: deleting a comment in the DB