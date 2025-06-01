from flask import Flask
from config import Config
from extensions import mongo, login_manager
from models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    mongo.init_app(app)
    login_manager.init_app(app)

    # Ensure database and collections exist
    with app.app_context():
        db = mongo.db
        if 'users' not in db.list_collection_names():
            db.create_collection('users')
        if 'items' not in db.list_collection_names():
            db.create_collection('items')
        if 'notifications' not in db.list_collection_names():
            db.create_collection('notifications')
            db.notifications.create_index([('user_id', 1), ('created_at', -1)])
        if 'feedback' not in db.list_collection_names():
            db.create_collection('feedback')
            db.feedback.create_index([('created_at', -1)])

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.items import items_bp
    from routes.admin import admin_bp
    from routes.general import general_bp
    from routes.feedback import feedback_bp
    from routes.notifications import notifications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(general_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(notifications_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
