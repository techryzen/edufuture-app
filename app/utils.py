from flask import current_app
from bson.objectid import ObjectId
import os
import secrets
from PIL import Image

def get_user_by_id(user_id):
    """Get a user by ID from MongoDB"""
    if not user_id:
        return None
    
    try:
        from app import mongo
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return user
    except Exception as e:
        current_app.logger.error(f"Error getting user: {e}")
        return None

def save_picture(form_picture, folder):
    """Save a picture and return the filename"""
    if not form_picture:
        return None
        
    # Generate a random filename to avoid collisions
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_extension
    
    # Create the full path to save the image
    picture_path = os.path.join(current_app.root_path, '..', 'static', 'uploads', folder, picture_filename)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    
    # Resize image to save space and load time
    output_size = (800, 800)  # Maximum dimensions
    i = Image.open(form_picture)
    
    # Preserve aspect ratio
    i.thumbnail(output_size)
    
    # Save the picture
    i.save(picture_path)
    
    return picture_filename

def save_image(form_picture, folder):
    """Alias for save_picture for backward compatibility"""
    return save_picture(form_picture, folder)

def allowed_file(filename, allowed_extensions):
    """Check if a file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def format_date(date):
    """Format a datetime object to a string"""
    if not date:
        return ""
    return date.strftime("%B %d, %Y")

def get_post_count_by_author(author_id):
    """Get the number of posts by an author"""
    try:
        from app import mongo
        count = mongo.db.blog_posts.count_documents({'author_id': ObjectId(author_id)})
        return count
    except Exception as e:
        current_app.logger.error(f"Error getting post count: {e}")
        return 0 