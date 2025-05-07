from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash, send_from_directory
from app.models.blog import Blog
from flask_login import current_user
from app import mongo
from datetime import datetime
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, '../static/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main_bp.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(current_app.root_path, '../static'), filename)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    # Render the index.html file as a template
    return render_template('index.html')

@main_bp.route('/about')
def about():
    return render_template('main/about.html', title="About Us | EduFuture")

@main_bp.route('/services')
def services():
    return render_template('main/services.html', title="Our Services | EduFuture")

@main_bp.route('/testimonials')
def testimonials():
    return render_template('main/testimonials.html', title="Testimonials | EduFuture")

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Process contact form submission
        contact_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'subject': request.form.get('subject'),
            'message': request.form.get('message'),
            'date': datetime.utcnow()
        }
        
        # Save to database
        mongo.db.contacts.insert_one(contact_data)
        
        # Flash a success message
        flash('Your message has been sent. We will contact you soon!', 'success')
        return redirect(url_for('main.contact'))
        
    return render_template('main/contact.html', title="Contact Us | EduFuture")

@main_bp.route('/search')
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('main.home'))
    
    # Perform text search on blog posts
    results = mongo.db.blog_posts.find({
        '$text': {'$search': query},
        'status': 'published'
    }).sort('created_at', -1)
    
    return render_template('main/search_results.html', 
                           results=list(results),
                           query=query,
                           title=f"Search: {query} | EduFuture") 