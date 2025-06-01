from extensions import mongo
from datetime import datetime
from bson import ObjectId

class Item:
    STATUS_CHOICES = ['lost', 'found', 'claimed', 'returned']
    CLAIM_STATUS_CHOICES = ['pending', 'approved', 'rejected']
    
    def __init__(self, item_data):
        self.id = str(item_data.get('_id'))
        self.title = item_data.get('title')
        self.description = item_data.get('description')
        self.location = item_data.get('location')
        self.category = item_data.get('category')
        self.status = item_data.get('status')
        self.reporter_id = item_data.get('reporter_id')
        self.reporter_name = item_data.get('reporter_name')
        self.report_date = item_data.get('report_date')
        self.claim_requests = item_data.get('claim_requests', [])

    @staticmethod
    def create_claim_request(item_id, user_id, username, message):
        request_data = {
            'user_id': str(user_id),
            'username': username,
            'message': message,
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        
        mongo.db.items.update_one(
            {'_id': ObjectId(item_id)},
            {'$push': {'claim_requests': request_data}}
        )
        return request_data

    @staticmethod
    def validate_claim(item_id, user_id):
        item = mongo.db.items.find_one({'_id': ObjectId(item_id)})
        if not item:
            return False, "Item not found"
        if item['status'] != 'found':
            return False, "Item is not available for claiming"
        if str(item['reporter_id']) == str(user_id):
            return False, "You cannot claim your own item"
        existing_claim = next(
            (claim for claim in item.get('claim_requests', []) 
             if claim['user_id'] == str(user_id)),
            None
        )
        if existing_claim:
            return False, "You have already submitted a claim for this item"
        return True, None