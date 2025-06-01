from flask import Flask
from config import Config
from extensions import mongo, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize MongoDB
    mongo.init_app(app)
    
    # Initialize LoginManager
    login_manager.init_app(app)

    # Ensure database and collections exist
    with app.app_context():
        db = mongo.db
        if 'users' not in db.list_collection_names():
            db.create_collection('users')
        if 'items' not in db.list_collection_names():
            db.create_collection('items')
        if 'feedback' not in db.list_collection_names():
            db.create_collection('feedback')

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.items import items_bp
    from routes.admin import admin_bp
    from routes.general import general_bp
    from routes.feedback import feedback_bp  # Add this line

    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(general_bp)
    app.register_blueprint(feedback_bp)  # Add this line

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
