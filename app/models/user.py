from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data
        
    def get_id(self):
        return str(self.user_data.get('_id'))
    
    @property
    def is_admin(self):
        return self.user_data.get('role') == 'admin'
    
    @property
    def username(self):
        return self.user_data.get('username')
    
    @property
    def email(self):
        return self.user_data.get('email')
        
    @property
    def profile_image(self):
        return self.user_data.get('profile_image', 'default_profile.jpg')
    
    @staticmethod
    def create_user(mongo, username, email, password, role='user'):
        """Create a new user in the database"""
        if mongo.db.users.find_one({'$or': [{'username': username}, {'email': email}]}):
            return None  # User already exists
            
        user_data = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'role': role,
            'profile_image': 'default_profile.jpg',
            'created_at': datetime.utcnow()
        }
        
        user_id = mongo.db.users.insert_one(user_data).inserted_id
        user_data['_id'] = user_id
        return User(user_data)
    
    @staticmethod
    def authenticate(mongo, email, password):
        """Authenticate a user by email and password"""
        user_data = mongo.db.users.find_one({'email': email})
        if user_data and check_password_hash(user_data['password'], password):
            return User(user_data)
        return None 