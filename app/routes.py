from flask import Blueprint, request, jsonify
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
    # Log the incoming JSON data from the frontend || TODO remove print log
    login_data = request.get_json()
    username = login_data.get("username")
    password = login_data.get("password")
    email = login_data.get("email")

    print("Received data:", login_data)

    username = username.lower()
    password = password.lower()
    email = email.lower()

    # Get users collection from DB
    db = get_db()
    users = db.users

    # Find user in DB by username or email
    user = users.find_one({"$or": [{"username": username}, {"email": email}]})

    if not user:
      return jsonify({"error": "User not found"}), 404
    
    # Check if password matches password stored in DB
    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
      return jsonify({"message": "Login successful"}), 200
    else:
      return jsonify({"error": "Invalid password"}), 400
  
  except Exception as e:
    print(f"Error during login: {e}")
    return jsonify({"error": "An error ocurred during login"}), 500

      


# API endpoint 3: updating a user in the DB
# API endpoint 4: deleting a user in the DB

# API endpoint 5: adding a recipe in the DB
# API endpoint 6: updating a recipe in the DB
# API endpoint 7: deleting a recipe in the DB

# API endpoint 8: adding a comment in the DB
# API endpoint 9: updating a comment in the DB
# API endpoint 10: deleting a comment in the DB