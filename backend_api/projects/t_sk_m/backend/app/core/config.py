"""App config"""
import os
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
