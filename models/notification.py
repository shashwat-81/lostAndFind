from extensions import mongo
from datetime import datetime
from bson import ObjectId

class Notification:
    def __init__(self, user_id, message, item_id=None, read=False):
        self.user_id = str(user_id)
        self.message = message
        self.item_id = str(item_id) if item_id else None
        self.read = read
        self.created_at = datetime.utcnow()

    def save(self):
        notification_data = {
            'user_id': self.user_id,
            'message': self.message,
            'item_id': self.item_id,
            'read': self.read,
            'created_at': self.created_at
        }
        result = mongo.db.notifications.insert_one(notification_data)
        return str(result.inserted_id)

    @staticmethod
    def get_user_notifications(user_id):
        return list(mongo.db.notifications.find(
            {'user_id': str(user_id)}
        ).sort('created_at', -1))

    @staticmethod
    def mark_as_read(notification_id):
        mongo.db.notifications.update_one(
            {'_id': ObjectId(notification_id)},
            {'$set': {'read': True}}
        )

    @staticmethod
    def get_unread_count(user_id):
        return mongo.db.notifications.count_documents({
            'user_id': str(user_id),
            'read': False
        })