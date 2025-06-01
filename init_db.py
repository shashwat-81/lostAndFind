from pymongo import MongoClient, ASCENDING, DESCENDING
from werkzeug.security import generate_password_hash
import datetime

def init_database():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    
    # Drop existing database if it exists
    client.drop_database('lost_and_found')
    
    # Create/Get database
    db = client['lost_and_found']
    
    # Create collections with validation
    db.create_collection('users')
    db.create_collection('items')
    db.create_collection('feedback')
    
    # Create indexes
    db.users.create_index('username', unique=True)
    db.items.create_index([('status', ASCENDING), ('category', ASCENDING)])
    db.items.create_index([('report_date', DESCENDING)])
    
    # Add schema validation for items collection
    db.command({
        'collMod': 'items',
        'validator': {
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ['title', 'description', 'category', 'location', 'status', 'report_date', 'reporter_id'],
                'properties': {
                    'title': {'bsonType': 'string'},
                    'description': {'bsonType': 'string'},
                    'category': {
                        'enum': ['Electronics', 'Clothing', 'Documents', 'Accessories', 'Other']
                    },
                    'location': {'bsonType': 'string'},
                    'status': {
                        'enum': ['lost', 'found']
                    },
                    'report_date': {'bsonType': 'date'},
                    'reporter_id': {'bsonType': 'string'},
                    'reporter_name': {'bsonType': 'string'}
                }
            }
        }
    })
    
    # Create feedback collection with validation
    db.command({
        'collMod': 'feedback',
        'validator': {
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ['user_id', 'message', 'created_at'],
                'properties': {
                    'user_id': {'bsonType': 'string'},
                    'message': {'bsonType': 'string'},
                    'category': {
                        'enum': ['bug', 'suggestion', 'complaint', 'other']
                    },
                    'created_at': {'bsonType': 'date'},
                    'status': {
                        'enum': ['new', 'in-progress', 'resolved']
                    }
                }
            }
        }
    })
    
    # Insert admin user
    admin_user = {
        'username': 'admin',
        'password_hash': generate_password_hash('admin123'),
        'role': 'admin',
        'created_at': datetime.datetime.utcnow()
    }
    db.users.insert_one(admin_user)
    
    # Insert sample items
    sample_items = [
        {
            'title': 'iPhone 13',
            'description': 'Black iPhone 13 with red case',
            'category': 'Electronics',
            'location': 'Library',
            'status': 'lost',
            'report_date': datetime.datetime.utcnow(),
            'reporter_id': str(admin_user['_id']),
            'reporter_name': 'admin'
        },
        {
            'title': 'Student ID Card',
            'description': 'University ID card',
            'category': 'Documents',
            'location': 'Cafeteria',
            'status': 'found',
            'report_date': datetime.datetime.utcnow(),
            'reporter_id': str(admin_user['_id']),
            'reporter_name': 'admin'
        }
    ]
    db.items.insert_many(sample_items)
    
    print("Database initialized successfully!")
    print("Admin credentials - Username: admin, Password: admin123")
    print("Sample items added to the database")

if __name__ == '__main__':
    init_database()