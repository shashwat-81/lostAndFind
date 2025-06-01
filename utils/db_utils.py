from extensions import mongo
from datetime import datetime
from bson import ObjectId

def get_filtered_items(category=None, status=None):
    """
    Get items with optional category and status filters
    """
    query = {}
    
    if category and category != 'all':
        query['category'] = category
        
    if status and status != 'all':
        query['status'] = status

    items = mongo.db.items.find(query).sort('report_date', -1)
    return list(items)

def add_item(item_data, user):
    item = {
        'title': item_data['title'],
        'description': item_data['description'],
        'category': item_data['category'],
        'location': item_data['location'],
        'status': item_data['status'],
        'report_date': datetime.utcnow(),
        'reporter_id': str(user.id),
        'reporter_name': user.username
    }
    return mongo.db.items.insert_one(item)