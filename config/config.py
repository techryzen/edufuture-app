import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set environment variables
os.environ["FLASK_ENV"] = "production"
os.environ["MONGO_URI"] = "mongodb+srv://rishab0909:1234@cluster0.7icfipp.mongodb.net/edufuture?retryWrites=true&w=majority&appName=Cluster0"
os.environ["SECRET_KEY"] = "your-secure-secret-key"
# Add any other environment variables you need

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'education_consultancy_secret_key')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://rishab0909:1234@cluster0.7icfipp.mongodb.net/edufuture?retryWrites=true&w=majority&appName=Cluster0')
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Admin account to be created at first run
    ADMIN_USERNAME = 'admin'
    ADMIN_EMAIL = 'admin@edufuture.com'
    ADMIN_PASSWORD = 'admin123'  # This would be hashed when creating the user
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
# Select configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 