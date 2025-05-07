from datetime import datetime
from bson.objectid import ObjectId

class Blog:
    @staticmethod
    def create_post(mongo, title, content, author_id, image_filename=None, tags=None, status='published'):
        """Create a new blog post"""
        post_data = {
            'title': title,
            'content': content,
            'author_id': ObjectId(author_id),
            'image': image_filename,
            'tags': tags or [],
            'status': status,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'views': 0,
            'likes': 0,
            'comments': []
        }
        
        post_id = mongo.db.blog_posts.insert_one(post_data).inserted_id
        return str(post_id)
    
    @staticmethod
    def get_post(mongo, post_id):
        """Get a blog post by ID"""
        return mongo.db.blog_posts.find_one({'_id': ObjectId(post_id)})
    
    @staticmethod
    def get_all_posts(mongo, status='published', limit=None, skip=0, sort_by='created_at', sort_order=-1):
        """Get all blog posts with pagination and sorting"""
        query = {'status': status}
        cursor = mongo.db.blog_posts.find(query).sort(sort_by, sort_order).skip(skip)
        
        if limit:
            cursor = cursor.limit(limit)
            
        return list(cursor)
    
    @staticmethod
    def get_posts_by_author(mongo, author_id, status=None, limit=None):
        """Get posts by a specific author"""
        query = {'author_id': ObjectId(author_id)}
        
        if status:
            query['status'] = status
            
        cursor = mongo.db.blog_posts.find(query).sort('created_at', -1)
        
        if limit:
            cursor = cursor.limit(limit)
            
        return list(cursor)
    
    @staticmethod
    def update_post(mongo, post_id, title, content, image_filename=None, tags=None, status='published'):
        """Update an existing blog post"""
        update_data = {
            'title': title,
            'content': content,
            'status': status,
            'updated_at': datetime.utcnow()
        }
        
        if image_filename:
            update_data['image'] = image_filename
            
        if tags is not None:
            update_data['tags'] = tags
            
        result = mongo.db.blog_posts.update_one(
            {'_id': ObjectId(post_id)},
            {'$set': update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def delete_post(mongo, post_id):
        """Delete a blog post"""
        result = mongo.db.blog_posts.delete_one({'_id': ObjectId(post_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def add_comment(mongo, post_id, user_id, content):
        """Add a comment to a blog post"""
        comment = {
            'user_id': ObjectId(user_id),
            'content': content,
            'created_at': datetime.utcnow()
        }
        
        result = mongo.db.blog_posts.update_one(
            {'_id': ObjectId(post_id)},
            {'$push': {'comments': comment}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def increment_view(mongo, post_id):
        """Increment the view count of a post"""
        mongo.db.blog_posts.update_one(
            {'_id': ObjectId(post_id)},
            {'$inc': {'views': 1}}
        )
    
    @staticmethod
    def toggle_like(mongo, post_id, user_id):
        """Toggle a like on a post"""
        # Check if the user already liked the post
        post = mongo.db.blog_posts.find_one(
            {'_id': ObjectId(post_id), 'liked_by': ObjectId(user_id)}
        )
        
        if post:
            # User already liked the post, remove the like
            result = mongo.db.blog_posts.update_one(
                {'_id': ObjectId(post_id)},
                {'$pull': {'liked_by': ObjectId(user_id)}, '$inc': {'likes': -1}}
            )
        else:
            # User hasn't liked the post, add the like
            result = mongo.db.blog_posts.update_one(
                {'_id': ObjectId(post_id)},
                {'$addToSet': {'liked_by': ObjectId(user_id)}, '$inc': {'likes': 1}}
            )
            
        return result.modified_count > 0 