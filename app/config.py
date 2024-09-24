import os
from dotenv import load_dotenv

# Loads environment variables from .env file
load_dotenv()

class Config:
  MONGODB_URI = os.getenv("MONGODB_URI")
  SECRET_KEY = os.getenv("SECRET_KEY")
  SESSION_COOKIE_NAME = 'session'
  SESSION_COOKIE_SAMESITE = 'None' # TODO Change to 'None' for deployment?
  SESSION_COOKIE_SECURE = False # TODO Change to 'True' for deployment
  SESSION_PERMANENT = False

  CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
  CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
  CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")