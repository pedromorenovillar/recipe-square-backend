from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from .db import get_db
from pymongo.errors import PyMongoError
import bcrypt

user_routes = Blueprint('user_routes', __name__)

# API endpoint 1: registering a user in the DB
@user_routes.route('/register_user', methods=['POST'])
def register_user():
  try:
    # Log the incoming JSON data from the frontend || TO DO remove print log
    user_data = request.get_json()
    print("Received data:", user_data)
    hashed_password = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())

    user_data["username"] = user_data["username"].lower()
    user_data["email"] = user_data["email"].lower()

    # Get users collection from DB
    db = get_db()
    users = db.users

    # Check if the username or email already exists in the database || TO DO remove print log
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
    # TO DO remove logs
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

    print("Received data:", login_data)  # TO DO: remove log

    db = get_db()
    users = db.users

    user = users.find_one({"$or": [{"username": username}, {"email": email}]})

    if not user:
      return jsonify({"error": "User not found"}), 404

    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
      # Log user details before setting session
      print(f"User authenticated: {user['username']}, Admin status: {user.get('is_admin', False)}")
      session['user_id'] = str(user['_id'])
      session['username'] = user['username']
      session['is_admin'] = user.get('is_admin', False)

      # Log session data
      print("Session data after login:", dict(session))

      return jsonify({
        "message": "Login successful",
        "is_admin": session['is_admin']
      }), 200
    else:
      return jsonify({"error": "Invalid password"}), 400

  except Exception as e:
    print(f"Error during login: {e}")
    return jsonify({"error": "An error occurred during login"}), 500

# Check if user is logged in
@user_routes.route('/check_session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        db = get_db()
        users = db.users
        user_id = session['user_id']
        
        # Convert string to ObjectId
        try:
            user_id = ObjectId(user_id)
        except Exception as e:
            print(f"Error converting user_id to ObjectId: {e}")
            return jsonify({'logged_in': False, 'is_admin': False}), 200

        user = users.find_one({"_id": user_id})

        print("Session data during check_session:", dict(session))
        print("User fetched from DB:", user)

        if user:
            is_admin = user.get('is_admin', False)
            username = user.get('username', 'unknown')
            return jsonify({
                'logged_in': True,
                'is_admin': is_admin,
                'username': username,
            })
        else:
            return jsonify({
                'logged_in': False,
                'is_admin': False
            }), 200
    else:
        return jsonify({
            'logged_in': False,
            'is_admin': False
        }), 200


# Log user out
@user_routes.route('/logout', methods=['POST'])
def logout():
    session.clear()
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