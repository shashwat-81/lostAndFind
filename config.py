import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change_this_secret_key'
    MONGO_URI = 'mongodb://localhost:27017/lost_and_found'
    MONGO_DBNAME = 'lost_and_found'
    MONGO_TZ_AWARE = True
