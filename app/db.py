from pymongo import MongoClient
import os

db = None

def init_db(app):
  global db
  MONGODB_URI = os.getenv('MONGODB_URI')
  client = MongoClient(MONGODB_URI)
  db = client.get_database("recipe_square")
  # TODO change DB name when final DB is implemented

def get_db():
  return db