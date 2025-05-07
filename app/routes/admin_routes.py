from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from bson.objectid import ObjectId
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import json
import random
from app import mongo
from app.utils import save_picture
from app.models.user import User
from app.models.blog import BlogPost
from app.models.notification import Notification
from app.forms.blog_forms import BlogPostForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin authorization decorator
def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You must be an admin to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    # Get counts for dashboard
    user_count = mongo.db.users.count_documents({})
    post_count = mongo.db.blog_posts.count_documents({})
    
    # Get recent posts
    recent_posts = list(mongo.db.blog_posts.find().sort('created_at', -1).limit(5))
    
    # Get recent users
    recent_users = list(mongo.db.users.find().sort('created_at', -1).limit(5))
    
    # Generate some analytics data for the charts
    today = datetime.utcnow()
    
    # Last 7 days post counts
    post_analytics = []
    for i in range(7):
        date = today - timedelta(days=i)
        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        count = mongo.db.blog_posts.count_documents({
            'created_at': {'$gte': start_of_day, '$lte': end_of_day}
        })
        
        post_analytics.append({
            'date': start_of_day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Generate mock data for user registrations over the last 7 days
    user_analytics = []
    for i in range(7):
        date = today - timedelta(days=i)
        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        count = mongo.db.users.count_documents({
            'created_at': {'$gte': start_of_day, '$lte': end_of_day}
        })
        
        user_analytics.append({
            'date': start_of_day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    return render_template('admin/dashboard.html', 
                          user_count=user_count, 
                          post_count=post_count, 
                          recent_posts=recent_posts,
                          recent_users=recent_users,
                          post_analytics=json.dumps(post_analytics),
                          user_analytics=json.dumps(user_analytics))

# User management routes
@admin_bp.route('/users')
@login_required
@admin_required
def user_list():
    page = request.args.get('page', 1, type=int)
    limit = 10
    skip = (page - 1) * limit
    
    search_query = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    # Build query
    query = {}
    
    if search_query:
        query['$or'] = [
            {'username': {'$regex': search_query, '$options': 'i'}},
            {'email': {'$regex': search_query, '$options': 'i'}}
        ]
    
    if role_filter:
        query['role'] = role_filter
    
    # Get total count for pagination
    total_users = mongo.db.users.count_documents(query)
    total_pages = (total_users // limit) + (1 if total_users % limit > 0 else 0)
    
    # Get users with pagination
    users = list(mongo.db.users.find(query).skip(skip).limit(limit))
    
    return render_template('admin/users/list.html', 
                          users=users, 
                          page=page, 
                          total_pages=total_pages,
                          search_query=search_query,
                          role_filter=role_filter)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        
        # Check if user already exists
        if mongo.db.users.find_one({'$or': [{'username': username}, {'email': email}]}):
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('admin.add_user'))
        
        # Handle profile image
        profile_image = 'default_profile.jpg'
        if 'profile_image' in request.files and request.files['profile_image'].filename:
            profile_image = save_picture(request.files['profile_image'], 'profile_pics')
            
        # Create user
        user_data = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'role': role,
            'profile_image': profile_image,
            'created_at': datetime.utcnow()
        }
        
        mongo.db.users.insert_one(user_data)
        flash('User created successfully.', 'success')
        return redirect(url_for('admin.user_list'))
    
    return render_template('admin/users/add.html')

@admin_bp.route('/users/edit/<user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.user_list'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role', 'user')
        
        # Check if username or email already exists for other users
        existing_user = mongo.db.users.find_one({
            '$and': [
                {'_id': {'$ne': ObjectId(user_id)}},
                {'$or': [{'username': username}, {'email': email}]}
            ]
        })
        
        if existing_user:
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        # Prepare update data
        update_data = {
            'username': username,
            'email': email,
            'role': role,
            'updated_at': datetime.utcnow()
        }
        
        # Handle password update
        new_password = request.form.get('password')
        if new_password:
            update_data['password'] = generate_password_hash(new_password)
        
        # Handle profile image
        if 'profile_image' in request.files and request.files['profile_image'].filename:
            update_data['profile_image'] = save_picture(request.files['profile_image'], 'profile_pics')
        
        # Update user
        mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.user_list'))
    
    return render_template('admin/users/edit.html', user=user)

@admin_bp.route('/users/delete/<user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    # Prevent deletion of current user
    if str(current_user.get_id()) == user_id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.user_list'))
    
    mongo.db.users.delete_one({'_id': ObjectId(user_id)})
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.user_list'))

# Blog management routes
@admin_bp.route('/blog')
@login_required
@admin_required
def blog_list():
    page = request.args.get('page', 1, type=int)
    limit = 10
    skip = (page - 1) * limit
    
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    sort = request.args.get('sort', 'newest')
    
    # Build query
    query = {}
    
    if search_query:
        query['$or'] = [
            {'title': {'$regex': search_query, '$options': 'i'}},
            {'content': {'$regex': search_query, '$options': 'i'}}
        ]
    
    if status_filter:
        query['status'] = status_filter
        
    if category_filter:
        query['category'] = ObjectId(category_filter)
    
    # Get total count for pagination
    total_posts = mongo.db.blog_posts.count_documents(query)
    total_pages = (total_posts // limit) + (1 if total_posts % limit > 0 else 0)
    
    # Determine sort order
    sort_order = [('created_at', -1)]  # default newest first
    if sort == 'oldest':
        sort_order = [('created_at', 1)]
    elif sort == 'a-z':
        sort_order = [('title', 1)]
    elif sort == 'z-a':
        sort_order = [('title', -1)]
    elif sort == 'most-views':
        sort_order = [('views', -1)]
    
    # Get posts with pagination
    posts = list(mongo.db.blog_posts.find(query).sort(sort_order).skip(skip).limit(limit))
    
    # Get authors for posts and attach author info to posts
    author_ids = []
    for post in posts:
        if 'author_id' in post and post['author_id']:
            # Convert ObjectId to string for dict key
            author_id = str(post['author_id']) if isinstance(post['author_id'], ObjectId) else post['author_id']
            author_ids.append(ObjectId(author_id))
    
    authors = {}
    if author_ids:
        for author in mongo.db.users.find({'_id': {'$in': author_ids}}):
            authors[str(author['_id'])] = {
                'username': author.get('username', 'Unknown'),
                'profile_image': author.get('profile_image', 'default_profile.jpg')
            }
    
    # Attach author info to posts
    for post in posts:
        if 'author_id' in post and post['author_id']:
            author_id = str(post['author_id']) if isinstance(post['author_id'], ObjectId) else post['author_id']
            if author_id in authors:
                if 'author_info' not in post or not post['author_info']:
                    post['author_info'] = authors[author_id]
            else:
                post['author_info'] = {'username': 'Unknown', 'profile_image': 'default_profile.jpg'}
        else:
            post['author_info'] = {'username': 'Unknown', 'profile_image': 'default_profile.jpg'}
    
    # Get categories for the category filter
    categories = list(mongo.db.categories.find())
    
    # Get post counts for each category
    category_post_counts = {}
    for category in categories:
        count = mongo.db.blog_posts.count_documents({'category': category['_id']})
        category_post_counts[str(category['_id'])] = count
    
    return render_template('admin/blog/list.html', 
                          posts=posts, 
                          authors=authors,
                          categories=categories,
                          category_post_counts=category_post_counts,
                          page=page, 
                          total_pages=total_pages,
                          search_query=search_query,
                          status_filter=status_filter,
                          category_filter=category_filter,
                          sort=sort)

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    # Get top posts by views
    top_posts_by_views = list(mongo.db.blog_posts.find().sort('views', -1).limit(5))
    
    # Get top posts by likes
    top_posts_by_likes = list(mongo.db.blog_posts.find().sort('likes', -1).limit(5))
    
    # Get user registration statistics by month
    current_year = datetime.utcnow().year
    user_registrations_by_month = []
    
    for month in range(1, 13):
        start_date = datetime(current_year, month, 1)
        if month == 12:
            end_date = datetime(current_year + 1, 1, 1)
        else:
            end_date = datetime(current_year, month + 1, 1)
        
        count = mongo.db.users.count_documents({
            'created_at': {'$gte': start_date, '$lt': end_date}
        })
        
        user_registrations_by_month.append({
            'month': start_date.strftime('%B'),
            'count': count
        })
    
    # Get post statistics by month
    post_stats_by_month = []
    
    for month in range(1, 13):
        start_date = datetime(current_year, month, 1)
        if month == 12:
            end_date = datetime(current_year + 1, 1, 1)
        else:
            end_date = datetime(current_year, month + 1, 1)
        
        count = mongo.db.blog_posts.count_documents({
            'created_at': {'$gte': start_date, '$lt': end_date}
        })
        
        post_stats_by_month.append({
            'month': start_date.strftime('%B'),
            'count': count
        })
    
    return render_template('admin/analytics.html',
                          top_posts_by_views=top_posts_by_views,
                          top_posts_by_likes=top_posts_by_likes,
                          user_registrations_by_month=json.dumps(user_registrations_by_month),
                          post_stats_by_month=json.dumps(post_stats_by_month))

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    if request.method == 'POST':
        # Handle site settings update
        site_title = request.form.get('site_title')
        site_description = request.form.get('site_description')
        contact_email = request.form.get('contact_email')
        posts_per_page = request.form.get('posts_per_page', 10)
        dark_mode_default = 'dark_mode_default' in request.form
        allow_comments = 'allow_comments' in request.form
        moderate_comments = 'moderate_comments' in request.form
        
        # Update site settings in database
        settings = mongo.db.settings.find_one({'type': 'site'})
        
        if settings:
            mongo.db.settings.update_one(
                {'type': 'site'},
                {'$set': {
                    'title': site_title,
                    'description': site_description,
                    'contact_email': contact_email,
                    'posts_per_page': int(posts_per_page),
                    'dark_mode_default': dark_mode_default,
                    'allow_comments': allow_comments,
                    'moderate_comments': moderate_comments,
                    'updated_at': datetime.utcnow()
                }}
            )
        else:
            mongo.db.settings.insert_one({
                'type': 'site',
                'title': site_title,
                'description': site_description,
                'contact_email': contact_email,
                'posts_per_page': int(posts_per_page),
                'dark_mode_default': dark_mode_default,
                'allow_comments': allow_comments,
                'moderate_comments': moderate_comments,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
        
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('admin.settings'))
    
    # Get current settings
    settings = mongo.db.settings.find_one({'type': 'site'}) or {
        'title': 'EduFuture',
        'description': 'Modern Education Consultancy',
        'contact_email': 'info@edufuture.com',
        'posts_per_page': 10,
        'dark_mode_default': False,
        'allow_comments': True,
        'moderate_comments': False
    }
    
    # Get email settings
    email_settings = mongo.db.settings.find_one({'type': 'email'})
    
    # Get security settings for current user
    security_settings = mongo.db.settings.find_one({'type': 'security', 'user_id': ObjectId(current_user.get_id())})
    
    # Get system logs (or provide empty list if not implemented)
    logs = []
    
    return render_template('admin/settings.html', 
                          settings=settings,
                          email_settings=email_settings,
                          security_settings=security_settings,
                          logs=logs)

@admin_bp.route('/settings/profile', methods=['POST'])
@login_required
@admin_required
def settings_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        bio = request.form.get('bio')
        twitter = request.form.get('twitter')
        linkedin = request.form.get('linkedin')
        
        # Check if username or email already exists for other users
        if username != current_user.username or email != current_user.email:
            existing_user = mongo.db.users.find_one({
                '$and': [
                    {'_id': {'$ne': ObjectId(current_user.get_id())}},
                    {'$or': [{'username': username}, {'email': email}]}
                ]
            })
            
            if existing_user:
                flash('Username or email already exists.', 'danger')
                return redirect(url_for('admin.settings'))
        
        # Prepare update data
        update_data = {
            'username': username,
            'email': email,
            'full_name': full_name,
            'bio': bio,
            'social': {
                'twitter': twitter,
                'linkedin': linkedin
            },
            'updated_at': datetime.utcnow()
        }
        
        # Handle profile image
        if 'profile_image' in request.files and request.files['profile_image'].filename:
            update_data['profile_image'] = save_picture(request.files['profile_image'], 'profile_pics')
        
        # Update user
        mongo.db.users.update_one({'_id': ObjectId(current_user.get_id())}, {'$set': update_data})
        
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('admin.settings'))
    
    # Should not reach here, as the form is submitted via POST
    return redirect(url_for('admin.settings'))

@admin_bp.route('/settings/email', methods=['POST'])
@login_required
@admin_required
def settings_email():
    if request.method == 'POST':
        smtp_host = request.form.get('smtp_host')
        smtp_port = request.form.get('smtp_port')
        smtp_security = request.form.get('smtp_security')
        smtp_username = request.form.get('smtp_username')
        smtp_password = request.form.get('smtp_password')
        from_email = request.form.get('from_email')
        from_name = request.form.get('from_name')
        
        # Update email settings in database
        email_settings = mongo.db.settings.find_one({'type': 'email'})
        
        email_data = {
            'smtp_host': smtp_host,
            'smtp_port': smtp_port,
            'smtp_security': smtp_security,
            'smtp_username': smtp_username,
            'from_email': from_email,
            'from_name': from_name,
            'updated_at': datetime.utcnow()
        }
        
        # Only update password if provided
        if smtp_password:
            email_data['smtp_password'] = smtp_password
        
        if email_settings:
            mongo.db.settings.update_one(
                {'type': 'email'},
                {'$set': email_data}
            )
        else:
            email_data['type'] = 'email'
            email_data['created_at'] = datetime.utcnow()
            if not smtp_password:
                email_data['smtp_password'] = ''
            mongo.db.settings.insert_one(email_data)
        
        flash('Email settings updated successfully.', 'success')
        return redirect(url_for('admin.settings'))
    
    # Should not reach here, as the form is submitted via POST
    return redirect(url_for('admin.settings'))

@admin_bp.route('/settings/security', methods=['POST'])
@login_required
@admin_required
def settings_security():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        enable_2fa = 'enable_2fa' in request.form
        login_notification = 'login_notification' in request.form
        
        # Check if we're changing password
        if current_password and new_password and confirm_password:
            # Verify current password
            user = mongo.db.users.find_one({'_id': ObjectId(current_user.get_id())})
            
            if not user or not check_password_hash(user['password'], current_password):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('admin.settings'))
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('admin.settings'))
            
            # Update password
            mongo.db.users.update_one(
                {'_id': ObjectId(current_user.get_id())},
                {'$set': {'password': generate_password_hash(new_password)}}
            )
            
            flash('Password updated successfully.', 'success')
        
        # Update security settings
        security_settings = mongo.db.settings.find_one({'type': 'security', 'user_id': ObjectId(current_user.get_id())})
        
        security_data = {
            'enable_2fa': enable_2fa,
            'login_notification': login_notification,
            'updated_at': datetime.utcnow()
        }
        
        if security_settings:
            mongo.db.settings.update_one(
                {'type': 'security', 'user_id': ObjectId(current_user.get_id())},
                {'$set': security_data}
            )
        else:
            security_data['type'] = 'security'
            security_data['user_id'] = ObjectId(current_user.get_id())
            security_data['created_at'] = datetime.utcnow()
            mongo.db.settings.insert_one(security_data)
        
        flash('Security settings updated successfully.', 'success')
        return redirect(url_for('admin.settings'))
    
    # Should not reach here, as the form is submitted via POST
    return redirect(url_for('admin.settings'))

@admin_bp.route('/roles')
@login_required
@admin_required
def role_list():
    # Get all roles (in a real app, this would be from the database)
    roles = [
        {'_id': 'admin', 'name': 'Administrator', 'description': 'Full access to all features'},
        {'_id': 'editor', 'name': 'Editor', 'description': 'Can manage content but not users'},
        {'_id': 'user', 'name': 'Standard User', 'description': 'Regular user with limited access'}
    ]
    
    return render_template('admin/roles/list.html', roles=roles)

@admin_bp.route('/notifications')
@login_required
@admin_required
def notifications():
    # Get notifications for admin
    notifications = list(mongo.db.notifications.find({
        '$or': [
            {'user_id': ObjectId(current_user.get_id())},
            {'role': 'admin'}
        ]
    }).sort('created_at', -1).limit(50))
    
    # Mark notifications as read
    mongo.db.notifications.update_many(
        {'user_id': ObjectId(current_user.get_id()), 'read': False},
        {'$set': {'read': True}}
    )
    
    return render_template('admin/notifications.html', notifications=notifications)

@admin_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
@admin_required
def mark_all_notifications_read():
    # Mark all notifications as read for the current user
    result = mongo.db.notifications.update_many(
        {'user_id': ObjectId(current_user.get_id()), 'read': False},
        {'$set': {'read': True}}
    )
    
    return jsonify({
        'success': True,
        'count': result.modified_count
    })

@admin_bp.route('/media')
@login_required
@admin_required
def media_library():
    # Get all uploaded media files
    # For simplicity, we'll just list files in the uploads folder
    uploads_dir = os.path.join(current_app.root_path, '..', 'static', 'uploads')
    media_files = []
    
    if os.path.exists(uploads_dir):
        for folder in ['blog', 'profile_pics']:
            folder_path = os.path.join(uploads_dir, folder)
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if os.path.isfile(os.path.join(folder_path, filename)):
                        file_path = os.path.join(folder, filename)
                        media_files.append({
                            'name': filename,
                            'path': file_path,
                            'url': url_for('static', filename=f'uploads/{file_path}'),
                            'type': folder
                        })
    
    return render_template('admin/media.html', media_files=media_files)

@admin_bp.route('/media/upload', methods=['POST'])
@login_required
@admin_required
def upload_media():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})
    
    if file:
        file_type = request.form.get('type', 'blog')
        filename = save_picture(file, file_type)
        
        return jsonify({
            'success': True, 
            'filename': filename,
            'url': url_for('static', filename=f'uploads/{file_type}/{filename}')
        })
    
    return jsonify({'success': False, 'message': 'File upload failed'})

@admin_bp.route('/media/delete/<path:filepath>', methods=['POST'])
@login_required
@admin_required
def delete_media(filepath):
    file_path = os.path.join(current_app.root_path, '..', 'static', 'uploads', filepath)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'File not found'})

# API endpoints for AJAX requests
@admin_bp.route('/api/stats/overview')
@login_required
@admin_required
def api_stats_overview():
    user_count = mongo.db.users.count_documents({})
    post_count = mongo.db.blog_posts.count_documents({})
    comment_count = sum(len(post.get('comments', [])) for post in mongo.db.blog_posts.find())
    
    # Get visitor count (mock data for this example)
    visitor_count = random.randint(100, 1000)
    
    return jsonify({
        'users': user_count,
        'posts': post_count,
        'comments': comment_count,
        'visitors': visitor_count
    })

@admin_bp.route('/api/notifications/unread')
@login_required
def api_unread_notifications():
    unread_count = mongo.db.notifications.count_documents({
        'user_id': ObjectId(current_user.get_id()),
        'read': False
    })
    
    return jsonify({'count': unread_count})

@admin_bp.route('/blog/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_blog():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        slug = request.form.get('slug')
        category = request.form.get('category')
        tags = [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        featured = 'featured' in request.form
        
        # Handle featured image
        featured_image = None
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file.filename != '':
                featured_image = save_picture(file, 'blog')
        
        # Create blog post
        post = {
            'title': title,
            'content': content,
            'slug': slug or title.lower().replace(' ', '-'),
            'category': ObjectId(category),
            'author_id': current_user.get_id(),
            'author_info': {
                'username': current_user.username,
                'profile_image': current_user.profile_image
            },
            'tags': tags,
            'featured': featured,
            'featured_image': featured_image,
            'status': 'published',
            'views': 0,
            'likes': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'comments': []
        }
        
        mongo.db.blog_posts.insert_one(post)
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('admin.blog_list'))
    
    # Get categories for the form
    categories = list(mongo.db.categories.find())
    return render_template('admin/blog/create.html', categories=categories)

@admin_bp.route('/blog/edit/<post_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_blog(post_id):
    post = mongo.db.blog_posts.find_one({'_id': ObjectId(post_id)})
    if not post:
        flash('Post not found', 'danger')
        return redirect(url_for('admin.blog_list'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        slug = request.form.get('slug')
        category = request.form.get('category')
        tags = [tag.strip() for tag in request.form.get('tags', '').split(',') if tag.strip()]
        featured = 'featured' in request.form
        
        # Handle featured image
        featured_image = post.get('featured_image')
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file.filename != '':
                featured_image = save_picture(file, 'blog')
        
        # Handle image removal
        if request.form.get('remove_image') == 'true':
            featured_image = None
        
        # Update blog post
        mongo.db.blog_posts.update_one(
            {'_id': ObjectId(post_id)},
            {'$set': {
                'title': title,
                'content': content,
                'slug': slug or title.lower().replace(' ', '-'),
                'category': ObjectId(category),
                'tags': tags,
                'featured': featured,
                'featured_image': featured_image,
                'updated_at': datetime.utcnow()
            }}
        )
        
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin.blog_list'))
    
    # Get categories for the form
    categories = list(mongo.db.categories.find())
    return render_template('admin/blog/create.html', post=post, categories=categories)

@admin_bp.route('/blog/delete/<post_id>', methods=['POST'])
@login_required
@admin_required
def delete_blog(post_id):
    # Get the post first to check if it exists
    post = mongo.db.blog_posts.find_one({'_id': ObjectId(post_id)})
    
    if not post:
        flash('Post not found', 'danger')
        return redirect(url_for('admin.blog_list'))
    
    # Delete the post
    mongo.db.blog_posts.delete_one({'_id': ObjectId(post_id)})
    
    # Delete associated image if it exists
    if post.get('featured_image'):
        try:
            image_path = os.path.join(current_app.root_path, '..', 'static', 'uploads', 'blog', post['featured_image'])
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            current_app.logger.error(f"Error deleting image: {e}")
    
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('admin.blog_list'))

@admin_bp.route('/category/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    name = request.form.get('name')
    slug = request.form.get('slug')
    
    if not name:
        flash('Category name is required', 'danger')
        return redirect(url_for('admin.blog_list'))
    
    # Generate slug if not provided
    if not slug:
        slug = name.lower().replace(' ', '-')
    
    # Check if category with same slug already exists
    existing = mongo.db.categories.find_one({'slug': slug})
    if existing:
        flash('A category with this slug already exists', 'danger')
        return redirect(url_for('admin.blog_list'))
    
    # Create category
    category = {
        'name': name,
        'slug': slug,
        'created_at': datetime.utcnow()
    }
    
    mongo.db.categories.insert_one(category)
    flash('Category added successfully!', 'success')
    return redirect(url_for('admin.blog_list'))

@admin_bp.route('/category/edit/<category_id>', methods=['POST'])
@login_required
@admin_required
def edit_category(category_id):
    name = request.form.get('name')
    slug = request.form.get('slug')
    
    if not name or not slug:
        flash('Category name and slug are required', 'danger')
        return redirect(url_for('admin.blog_list'))
    
    # Check if category with same slug already exists (but not this one)
    existing = mongo.db.categories.find_one({'slug': slug, '_id': {'$ne': ObjectId(category_id)}})
    if existing:
        flash('A category with this slug already exists', 'danger')
        return redirect(url_for('admin.blog_list'))
    
    # Update category
    mongo.db.categories.update_one(
        {'_id': ObjectId(category_id)},
        {'$set': {
            'name': name,
            'slug': slug,
            'updated_at': datetime.utcnow()
        }}
    )
    
    flash('Category updated successfully!', 'success')
    return redirect(url_for('admin.blog_list'))

@admin_bp.route('/category/delete/<category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    # Get the category to check if it exists
    category = mongo.db.categories.find_one({'_id': ObjectId(category_id)})
    
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('admin.blog_list'))
    
    # Get or create the "Uncategorized" category
    uncategorized = mongo.db.categories.find_one({'slug': 'uncategorized'})
    if not uncategorized:
        uncategorized_id = mongo.db.categories.insert_one({
            'name': 'Uncategorized',
            'slug': 'uncategorized',
            'created_at': datetime.utcnow()
        }).inserted_id
    else:
        uncategorized_id = uncategorized['_id']
    
    # Move all posts from this category to "Uncategorized"
    mongo.db.blog_posts.update_many(
        {'category': ObjectId(category_id)},
        {'$set': {'category': uncategorized_id}}
    )
    
    # Delete the category
    mongo.db.categories.delete_one({'_id': ObjectId(category_id)})
    
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin.blog_list'))

@admin_bp.route('/backup', methods=['POST'])
@login_required
@admin_required
def backup():
    """Create a backup of the database collections"""
    include_users = 'include_users' in request.form
    include_posts = 'include_posts' in request.form
    include_settings = 'include_settings' in request.form
    
    backup_data = {}
    
    if include_users:
        users = list(mongo.db.users.find({}, {'password': 0}))  # Exclude passwords
        # Convert ObjectId to string for JSON serialization
        for user in users:
            user['_id'] = str(user['_id'])
        backup_data['users'] = users
    
    if include_posts:
        posts = list(mongo.db.blog_posts.find({}))
        # Convert ObjectId to string for JSON serialization
        for post in posts:
            post['_id'] = str(post['_id'])
            if 'author_id' in post and post['author_id']:
                post['author_id'] = str(post['author_id'])
            if 'category' in post and post['category']:
                post['category'] = str(post['category'])
        backup_data['blog_posts'] = posts
        
        # Include categories
        categories = list(mongo.db.categories.find({}))
        for category in categories:
            category['_id'] = str(category['_id'])
        backup_data['categories'] = categories
    
    if include_settings:
        settings = list(mongo.db.settings.find({}))
        for setting in settings:
            setting['_id'] = str(setting['_id'])
            if 'user_id' in setting and setting['user_id']:
                setting['user_id'] = str(setting['user_id'])
        backup_data['settings'] = settings
    
    # Create JSON response with attachment
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    backup_json = json.dumps(backup_data, indent=2, default=str)
    
    response = current_app.response_class(
        backup_json,
        mimetype='application/json',
        headers={
            'Content-Disposition': f'attachment;filename=edufuture_backup_{timestamp}.json'
        }
    )
    
    return response

@admin_bp.route('/restore', methods=['POST'])
@login_required
@admin_required
def restore():
    """Restore the database from a backup file"""
    if 'backup_file' not in request.files:
        flash('No backup file selected', 'danger')
        return redirect(url_for('admin.settings'))
    
    file = request.files['backup_file']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('admin.settings'))
    
    if not file.filename.endswith('.json'):
        flash('Invalid file format. Please upload a .json backup file', 'danger')
        return redirect(url_for('admin.settings'))
    
    try:
        # Read and parse backup data
        backup_data = json.loads(file.read().decode('utf-8'))
        
        # Restore users
        if 'users' in backup_data:
            # Convert string IDs back to ObjectId for MongoDB
            for user in backup_data['users']:
                user['_id'] = ObjectId(user['_id'])
                # We don't restore user passwords for security
            
            # Delete all existing users and insert from backup
            # Note: This would normally need more careful handling to avoid data loss
            if backup_data['users']:
                mongo.db.users.delete_many({})
                mongo.db.users.insert_many(backup_data['users'])
        
        # Restore categories
        if 'categories' in backup_data:
            for category in backup_data['categories']:
                category['_id'] = ObjectId(category['_id'])
            
            if backup_data['categories']:
                mongo.db.categories.delete_many({})
                mongo.db.categories.insert_many(backup_data['categories'])
        
        # Restore blog posts
        if 'blog_posts' in backup_data:
            for post in backup_data['blog_posts']:
                post['_id'] = ObjectId(post['_id'])
                if 'author_id' in post and post['author_id']:
                    post['author_id'] = ObjectId(post['author_id'])
                if 'category' in post and post['category']:
                    post['category'] = ObjectId(post['category'])
            
            if backup_data['blog_posts']:
                mongo.db.blog_posts.delete_many({})
                mongo.db.blog_posts.insert_many(backup_data['blog_posts'])
        
        # Restore settings
        if 'settings' in backup_data:
            for setting in backup_data['settings']:
                setting['_id'] = ObjectId(setting['_id'])
                if 'user_id' in setting and setting['user_id']:
                    setting['user_id'] = ObjectId(setting['user_id'])
            
            if backup_data['settings']:
                mongo.db.settings.delete_many({})
                mongo.db.settings.insert_many(backup_data['settings'])
        
        flash('Database restored successfully!', 'success')
    except Exception as e:
        flash(f'Error restoring database: {str(e)}', 'danger')
    
    return redirect(url_for('admin.settings')) 