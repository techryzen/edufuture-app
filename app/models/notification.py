from datetime import datetime
from bson.objectid import ObjectId

class Notification:
    @staticmethod
    def create(mongo, message, user_id=None, user_role=None, link=None, category='info'):
        """
        Create a new notification
        
        Args:
            mongo: MongoDB instance
            message: Notification message text
            user_id: ID of the specific user (or None for role-based)
            user_role: Role to target (e.g., 'admin', 'user')
            link: Optional URL to link the notification to
            category: info, warning, success, danger
        """
        notification = {
            'message': message,
            'category': category,
            'created_at': datetime.utcnow(),
            'read': False,
            'link': link
        }
        
        if user_id:
            notification['user_id'] = ObjectId(user_id)
        
        if user_role:
            notification['role'] = user_role
            
        result = mongo.db.notifications.insert_one(notification)
        return str(result.inserted_id)
    
    @staticmethod
    def get_for_user(mongo, user_id, include_role=True, limit=50, only_unread=False):
        """Get notifications for a specific user"""
        query = {'$or': [{'user_id': ObjectId(user_id)}]}
        
        # Include role-based notifications if requested
        if include_role:
            # Get user's role first
            user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user and 'role' in user:
                query['$or'].append({'role': user['role']})
        
        # Filter to only unread if requested
        if only_unread:
            query['read'] = False
            
        # Get notifications
        notifications = list(
            mongo.db.notifications.find(query)
            .sort('created_at', -1)
            .limit(limit)
        )
        
        return notifications
    
    @staticmethod
    def mark_as_read(mongo, notification_id):
        """Mark a notification as read"""
        result = mongo.db.notifications.update_one(
            {'_id': ObjectId(notification_id)},
            {'$set': {'read': True}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def mark_all_as_read(mongo, user_id):
        """Mark all notifications for a user as read"""
        result = mongo.db.notifications.update_many(
            {'user_id': ObjectId(user_id), 'read': False},
            {'$set': {'read': True}}
        )
        
        return result.modified_count
    
    @staticmethod
    def delete(mongo, notification_id):
        """Delete a notification"""
        result = mongo.db.notifications.delete_one({'_id': ObjectId(notification_id)})
        return result.deleted_count > 0 