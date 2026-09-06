import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "casino-secret-key")
    DATABASE_URL = os.getenv("DATABASE_URL")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
