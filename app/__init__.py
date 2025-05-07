# Import necessary modules
import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from config.config import config
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId
from app.context_processors import inject_now
from app.utils import get_user_by_id, format_date, get_post_count_by_author
from datetime import datetime

# Initialize extensions
mongo = PyMongo()
login_manager = LoginManager()

def create_app(config_name='development'):
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='templates')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Set debug mode based on environment
    app.config['DEBUG'] = config_name == 'development'
    
    # Initialize extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Ensure upload directories exist
    os.makedirs(os.path.join(app.root_path, '../static/uploads/blog'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '../static/uploads/profile_pics'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '../static/uploads/media'), exist_ok=True)
    
    # Create initial admin user if not exists
    with app.app_context():
        if mongo.db.users.count_documents({'role': 'admin'}) == 0:
            admin_user = {
                'username': app.config['ADMIN_USERNAME'],
                'email': app.config['ADMIN_EMAIL'],
                'password': generate_password_hash(app.config['ADMIN_PASSWORD']),
                'role': 'admin',
                'profile_image': 'default_profile.jpg',
                'created_at': datetime.utcnow()
            }
            mongo.db.users.insert_one(admin_user)
            
        # Initialize categories if they don't exist
        if mongo.db.categories.count_documents({}) == 0:
            categories = [
                {'name': 'Education', 'slug': 'education'},
                {'name': 'Study Abroad', 'slug': 'study-abroad'},
                {'name': 'Test Preparation', 'slug': 'test-preparation'},
                {'name': 'Career Guidance', 'slug': 'career-guidance'},
                {'name': 'Uncategorized', 'slug': 'uncategorized'}
            ]
            mongo.db.categories.insert_many(categories)
        
        # Create text index on blog posts for search functionality
        mongo.db.blog_posts.create_index([
            ('title', 'text'),
            ('content', 'text'),
            ('tags', 'text')
        ])
    
    # Register context processors
    app.context_processor(inject_now)
    
    # Register template globals
    app.jinja_env.globals.update(
        get_user_by_id=get_user_by_id,
        format_date=format_date,
        get_post_count_by_author=get_post_count_by_author
    )
    
    # Import and register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.blog_routes import blog_bp
    from app.routes.main_routes import main_bp
    from app.routes.admin_routes import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user_data:
            return None
        return User(user_data)
    
    return app 