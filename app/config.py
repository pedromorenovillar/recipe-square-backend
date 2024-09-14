import os
from dotenv import load_dotenv

# Loads environment variables from .env file
load_dotenv()

class Config:
  MONGODB_URI = os.getenv("MONGODB_URI")