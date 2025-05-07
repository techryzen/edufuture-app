from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app.forms.auth_forms import LoginForm, RegistrationForm, ProfileUpdateForm
from app.models.user import User
from app import mongo

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = mongo.db.users.find_one({
            '$or': [
                {'username': form.username.data},
                {'email': form.email.data}
            ]
        })
        
        if existing_user:
            if existing_user.get('username') == form.username.data:
                flash('That username is already taken. Please choose a different one.', 'danger')
            else:
                flash('That email is already registered. Please log in or use a different email.', 'danger')
            return render_template('auth/register.html', title='Register', form=form)
        
        # Create new user
        user = User.create_user(
            mongo,
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(mongo, form.email.data, form.password.data)
        
        if user:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileUpdateForm()
    
    if form.validate_on_submit():
        # Verify current password
        user_data = mongo.db.users.find_one({'_id': current_user.id})
        if not check_password_hash(user_data['password'], form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.profile'))
        
        # Process profile image if uploaded
        if form.profile_image.data:
            image_filename = secure_filename(form.profile_image.data.filename)
            picture_path = os.path.join(current_app.root_path, 'static/uploads/profile_pics', image_filename)
            form.profile_image.data.save(picture_path)
        else:
            image_filename = user_data.get('profile_image', 'default_profile.jpg')
        
        # Update user data
        update_data = {
            'username': form.username.data,
            'email': form.email.data,
            'profile_image': image_filename,
            'updated_at': datetime.utcnow()
        }
        
        # Update password if new password provided
        if form.new_password.data:
            update_data['password'] = generate_password_hash(form.new_password.data)
        
        mongo.db.users.update_one(
            {'_id': current_user.id},
            {'$set': update_data}
        )
        
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('auth.profile'))
    
    elif request.method == 'GET':
        # Pre-fill form with current user data
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('auth/profile.html', title='Profile', form=form)

@auth_bp.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))
    
    # Get stats for admin dashboard
    user_count = mongo.db.users.count_documents({})
    post_count = mongo.db.blog_posts.count_documents({})
    contact_count = mongo.db.contacts.count_documents({})
    
    # Get recent contacts
    recent_contacts = list(mongo.db.contacts.find().sort('date', -1).limit(5))
    
    # Get recent users
    recent_users = list(mongo.db.users.find().sort('created_at', -1).limit(5))
    
    return render_template(
        'admin/dashboard.html',
        title='Admin Dashboard',
        user_count=user_count,
        post_count=post_count,
        contact_count=contact_count,
        recent_contacts=recent_contacts,
        recent_users=recent_users
    ) 