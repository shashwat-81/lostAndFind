from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask import current_app
from extensions import mongo
from models.notification import Notification

class User(UserMixin):
    def __init__(self, user_data):
        if user_data is None:
            raise ValueError('User data cannot be None')
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password_hash = user_data['password_hash']
        self.role = user_data.get('role', 'user')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        try:
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            return User(user_data) if user_data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    @staticmethod
    def find_by_username(username):
        try:
            user_data = mongo.db.users.find_one({'username': username})
            return User(user_data) if user_data else None
        except Exception as e:
            print(f"Error finding user: {e}")
            return None

    @staticmethod
    def create_user(username, password, role='user'):
        try:
            password_hash = generate_password_hash(password)
            user_data = {
                'username': username,
                'password_hash': password_hash,
                'role': role
            }
            result = mongo.db.users.insert_one(user_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def get_notifications(self):
        return Notification.get_user_notifications(self.id)

    def get_unread_notifications_count(self):
        return Notification.get_unread_count(self.id)
