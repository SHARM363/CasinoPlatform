import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "casino-secret-key")
    ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
