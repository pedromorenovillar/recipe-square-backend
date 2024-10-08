import os
from dotenv import load_dotenv

# Loads environment variables from .env file
load_dotenv()

class Config:
  MONGODB_URI = os.getenv("MONGODB_URI")
  SECRET_KEY = os.getenv("SECRET_KEY")
  SESSION_COOKIE_NAME = 'session'
  SESSION_COOKIE_SAMESITE = 'None'
  SESSION_COOKIE_SECURE = True
  SESSION_PERMANENT = False

  CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
  CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
  CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

  MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
  MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
  MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", 'True') == 'True'
  MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", 'False') == 'True'
  MAIL_USERNAME = os.getenv("MAIL_USERNAME")
  MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
  MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")  