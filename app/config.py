import os
from dotenv import load_dotenv

# Loads environment variables from .env file
load_dotenv()

class Config:
  MONGODB_URI = os.getenv("MONGODB_URI")
  SECRET_KEY = os.getenv("SECRET_KEY")
  SESSION_COOKIE_SAMESITE = 'Lax' # TODO Change to 'None' for deployment?
  SESSION_COOKIE_SECURE = False # TODO Change to 'True' for deployment
  SESSION_PERMANENT = False