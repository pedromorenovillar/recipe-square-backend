from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from bson.errors import InvalidId
from .db import get_db
from pymongo.errors import PyMongoError
import bcrypt
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from app.config import Config
from datetime import datetime, timezone
from pymongo import DESCENDING

cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET
)

user_routes = Blueprint('user_routes', __name__)

# API endpoint 1: registering a user in the DB
@user_routes.route('/register_user', methods=['POST'])
def register_user():
  try:
    user_data = request.get_json()
    hashed_password = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())
    user_data["email"] = user_data["email"].lower()

    db = get_db()
    users = db.users

    existing_user = users.find_one({"$or": [{"username": user_data["username"]}, {"email": user_data["email"]}]})
    
    if existing_user:
      return jsonify({"error": "Username or email already exists"}), 400

    new_user = {
        "username": user_data["username"],
        "email": user_data["email"],
        "password": hashed_password,
        "is_admin": user_data["is_admin"]
    }

    result = users.insert_one(new_user)

    return jsonify({f"message": "User registered successfully", "id": str(result.inserted_id)}), 201
  
  except PyMongoError as e:
    print(f"Error registering user into MongoDB: {e}")
    return jsonify({"error": "Database registration failed"}), 500

  except Exception as e:
    print(f"Unexpected error: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500
  
# API endpoint 2: logging in a user in the DB
@user_routes.route('/login_user', methods=['POST'])
def login_user():
  try:
    login_data = request.get_json()
    username = login_data.get("username").lower()
    password = login_data.get("password").lower()
    email = login_data.get("email").lower()

    db = get_db()
    users = db.users

    user = users.find_one({"$or": [{"username": username}, {"email": email}]})

    if not user:
      return jsonify({"error": "User not found"}), 404

    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
      session['user_id'] = str(user['_id'])
      session['username'] = user['username']
      session['is_admin'] = user.get('is_admin', False)

      return jsonify({
        "message": "Login successful",
        "is_admin": session['is_admin'],
        "user_id": session['user_id'],
        "username": session['username']
      }), 200
    else:
      return jsonify({"error": "Invalid password"}), 400

  except Exception as e:
    print(f"Error during login: {e}")
    return jsonify({"error": "An error occurred during login"}), 500

# API endpoint 3: logging a user out
@user_routes.route('/logout', methods=['POST'])
def logout():
    session.clear()
    response = jsonify({"message": "Logged out successfully"})
    
    response.set_cookie('session', '', expires=0, samesite='Lax', secure=False)
    return response

# API endpoint 4: getting all users from the DB
@user_routes.route('/get_all_users', methods=['GET'])
def get_all_users():
  try:
    db = get_db()
    users = db.users

    all_users = list(
            users.find(
              {}, 
              {"_id": 1, "username": 1, "email": 1, "is_admin": 1}
            )
        )
    for user in all_users:
        user["_id"] = str(user["_id"])
    return jsonify({"users": all_users}), 200
  
  except PyMongoError as e:
    print(f"Error getting users from MongoDB: {e}")
    return jsonify({"error": "Loading from database failed"}), 500

  except Exception as e:
    print(f"Unexpected error: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500
# API endpoint 5: updating user admin role in the DB
@user_routes.route('/update_user_role/<user_id>', methods=['PUT'])
def update_user_role(user_id):
  try:
    data = request.json
    print(data)
    updatedRole = data.get("is_admin")

    db = get_db()
    users = db.users
    result = users.update_one({"_id": ObjectId(user_id)}, {"$set": {"is_admin": updatedRole}})

    if result.modified_count == 1:
            return jsonify({"message": "User role updated successfully"}), 200
    else:
        return jsonify({"message": "User role update failed"}), 400

  except Exception as e:
      print(f"Error updating user role: {e}")
      return jsonify({"error": "An error occurred"}), 500
  
# API endpoint 6: deleting a user in the DB
@user_routes.route('/delete_user', methods=['DELETE'])
def delete_user():
    try:
        user_data = request.get_json()
        user_id = user_data.get("_id")
        
        if not user_id:
          return jsonify({"error": "User ID is required"}), 400

        db = get_db()
        users = db.users
        result = users.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count == 1:
          return jsonify({"message": "User deleted successfully"}), 200
        else:
          return jsonify({"error": "User not found"}), 404

    except Exception as e:
        print(f"Error deleting user: {e}")
        return jsonify({"error": "An error occurred deleting the user"}), 500
# API endpoint 7: adding a recipe in the DB
@user_routes.route('/add_recipe', methods=['POST'])
def add_recipe():
  try:
    recipe_data = request.get_json()

    db = get_db()
    recipes = db.recipes

    image_base64 = recipe_data.get("image")
    image_url = None

    if image_base64:
        upload_result = cloudinary.uploader.upload(f"data:image/png;base64,{image_base64}")

        image_url, _ = cloudinary_url(
            upload_result['public_id'],
            fetch_format="auto",  
            quality="auto",      
            crop="auto",         
            gravity="auto",       
            width=500,           
            height=500           
        )

    created_at = recipe_data.get('created_at', None)
    if created_at is None:
       created_at = datetime.now(datetime.timezone.utc)

    new_recipe = {
        "title": recipe_data["title"],
        "instructions": recipe_data["instructions"],
        "ingredients": recipe_data["ingredients"],
        "image": image_url,
        "user_id": recipe_data["user_id"],
        "created_at": created_at
    }

    result = recipes.insert_one(new_recipe)

    return jsonify({f"message": "Recipe saved successfully", "id": str(result.inserted_id)}), 201
  
  except PyMongoError as e:
    print(f"Error saving recipe into MongoDB: {e}")
    return jsonify({"error": "Saving to database failed"}), 500

  except Exception as e:
    print(f"Unexpected error: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500

# API endpoint 8: getting all recipes from the DB
@user_routes.route('/get_all_recipes', methods=['GET'])
def get_all_recipes():
  try:
    db = get_db()
    recipes = db.recipes

    all_recipes = list(
            recipes.find(
              {}, 
              {"user_id": 1, "title": 1, "image": 1, "_id": 1, "created_at": 1}
            ).sort("created_at", DESCENDING)
        )
    for recipe in all_recipes:
        recipe["_id"] = str(recipe["_id"])
    return jsonify({"recipes": all_recipes}), 200
  
  except PyMongoError as e:
    print(f"Error getting recipes from MongoDB: {e}")
    return jsonify({"error": "Loading from database failed"}), 500

  except Exception as e:
    print(f"Unexpected error: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500
  
# API endpoint 9: getting all recipes from a user from the DB
@user_routes.route('/get_all_recipes_from_user', methods=['GET'])
def get_all_recipes_from_user():
    try:
        user_id = request.args.get("user_id")

        db = get_db()
        recipes = db.recipes
        
        user_recipes = list(
            recipes.find(
                {"user_id": user_id}, 
                {"title": 1, "image": 1, "_id": 1, "created_at": 1}
            ).sort("created_at", DESCENDING)
        )

        if not user_recipes:
            return jsonify({"error": "Recipes not found"}), 404
        
        for recipe in user_recipes:
            recipe["_id"] = str(recipe["_id"])

        return jsonify({"recipes": user_recipes}), 200

    except Exception as e:
        print(f"Error loading recipes: {e}")
        return jsonify({"error": "An error occurred loading recipes"}), 500

# API endpoint 10: deleting a recipe from the DB
@user_routes.route('/delete_recipe', methods=['DELETE'])
def delete_recipe():
    try:
        recipe_data = request.get_json()
        print("recipe data:", recipe_data)
        recipe_id = recipe_data.get("_id")
        
        if not recipe_id:
          return jsonify({"error": "Recipe ID is required"}), 400

        db = get_db()
        result = db.recipes.delete_one({"_id": ObjectId(recipe_id)})

        if result.deleted_count == 1:
          return jsonify({"message": "Recipe deleted successfully"}), 200
        else:
          return jsonify({"error": "Recipe not found"}), 404

    except Exception as e:
        print(f"Error deleting recipe: {e}")
        return jsonify({"error": "An error occurred deleting the recipe"}), 500
    
# API endpoint 11: getting one recipe from the DB by its ID
@user_routes.route('/recipe/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    print('Received recipe ID:', recipe_id)
    db = get_db()
    recipes = db.recipes
    try:
        recipe = recipes.find_one({"_id": ObjectId(recipe_id)})
        if recipe:
            recipe['_id'] = str(recipe['_id'])
            return jsonify(recipe), 200
        else:
            return jsonify({"error": "Recipe not found"}), 404
    except InvalidId:
        return jsonify({"error": "Invalid recipe ID format"}), 400

# API endpoint 12: updating a recipe
@user_routes.route('/update_recipe/<recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    data = request.json
    db = get_db()
    recipes = db.recipes
    recipes.update_one({"_id": ObjectId(recipe_id)}, {"$set": data})
    return jsonify({"message": "Recipe updated successfully"})

# API endpoint 13: searching a recipe in the DB
@user_routes.route('/search_recipes/<searchKey>', methods=['GET'])
def search_recipes(searchKey):
    if searchKey:
        db = get_db()
        print(f"searchkey: {searchKey}")
        recipes = list(db.recipes.find({"title": {"$regex": searchKey, "$options": "i"}}))
        print(f"Found recipes: {recipes}")
        
        for recipe in recipes:
          recipe['_id'] = str(recipe['_id'])
        suggestions = [{"title": recipe["title"], "id": str(recipe["_id"]), "image": recipe["image"]} for recipe in recipes]
        print(f"Suggestions: {suggestions}")
        return jsonify(suggestions), 200
    return jsonify([]), 200

# API endpoint 14: searching 3 recipes with images in the DB
@user_routes.route('/get_three_random_recipes', methods=['GET'])
def get_three_random_recipes():
    try:
        db = get_db()
        recipes_collection = db.recipes

        pipeline = [
            {"$match": {"image": {"$exists": True, "$ne": None}}},
            {"$sample": {"size": 3}},
            {
                "$addFields": {
                    "user_id_obj": {"$convert": {"input": "$user_id", "to": "objectId", "onError": None}}
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id_obj",
                    "foreignField": "_id",
                    "as": "user_info"
                }
            },
            {"$unwind": "$user_info"},
            {
                "$project": {
                    "title": 1,
                    "image": 1,
                    "_id": 1,
                    "username": "$user_info.username"
                }
            }
        ]

        random_recipes = list(recipes_collection.aggregate(pipeline))
        
        for recipe in random_recipes:
            recipe["_id"] = str(recipe["_id"])
        
        return jsonify({"recipes": random_recipes}), 200

    except PyMongoError as e:
        print(f"Error getting random recipes from MongoDB: {e}")
        return jsonify({"error": "Loading from database failed"}), 500

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500