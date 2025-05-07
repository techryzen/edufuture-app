from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import current_user, login_required
from app.forms.blog_forms import BlogPostForm, CommentForm, BlogSearchForm
from app.models.blog import Blog
from app.utils import save_picture, get_post_count_by_author
import os
from datetime import datetime
from bson.objectid import ObjectId
from app import mongo

blog_bp = Blueprint('blog', __name__)

def save_blog_image(form_image):
    """Save blog post image to filesystem and return filename"""
    return save_picture(form_image, 'blog')

@blog_bp.route('/blog')
def blog_list():
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Number of posts per page
    skip = (page - 1) * per_page
    
    # Get total count for pagination
    total_posts = mongo.db.blog_posts.count_documents({'status': 'published'})
    total_pages = (total_posts + per_page - 1) // per_page  # Ceiling division
    
    # Get posts for current page
    posts = Blog.get_all_posts(mongo, limit=per_page, skip=skip)
    
    # Get categories/tags for sidebar
    tags = mongo.db.blog_posts.distinct('tags')
    
    # Get recent posts for sidebar
    recent_posts = Blog.get_all_posts(mongo, limit=3)
    
    return render_template(
        'blog/blog_list.html',
        title='Blog | EduFuture',
        posts=posts,
        page=page,
        total_pages=total_pages,
        tags=tags,
        recent_posts=recent_posts
    )

@blog_bp.route('/blog/post/<post_id>', methods=['GET', 'POST'])
def blog_detail(post_id):
    post = Blog.get_post(mongo, post_id)
    
    if not post:
        abort(404)
    
    # Get author information
    author = mongo.db.users.find_one({'_id': post['author_id']})
    
    # Get related posts (by tags)
    related_posts = []
    if post.get('tags'):
        related_posts = list(mongo.db.blog_posts.find({
            'tags': {'$in': post['tags']},
            '_id': {'$ne': ObjectId(post_id)},
            'status': 'published'
        }).limit(3))
    
    # Get author post count
    author_posts_count = get_post_count_by_author(post['author_id'])
    
    # Increment view count
    Blog.increment_view(mongo, post_id)
    
    # Handle comment form
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You need to be logged in to comment.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        
        # Add comment
        Blog.add_comment(mongo, post_id, current_user.get_id(), form.content.data)
        flash('Your comment has been added!', 'success')
        return redirect(url_for('blog.blog_detail', post_id=post_id))
    
    return render_template(
        'blog/blog_detail.html',
        title=post['title'] + ' | EduFuture',
        post=post,
        author=author,
        author_posts_count=author_posts_count,
        related_posts=related_posts,
        form=form
    )

@blog_bp.route('/blog/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = BlogPostForm()
    
    if form.validate_on_submit():
        image_filename = save_blog_image(form.image.data)
        
        # Process tags
        tags = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
        
        # Create blog post
        post_id = Blog.create_post(
            mongo,
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.get_id(),
            image_filename=image_filename,
            tags=tags,
            status=form.status.data
        )
        
        flash('Your blog post has been created!', 'success')
        return redirect(url_for('blog.blog_detail', post_id=post_id))
    
    return render_template('blog/blog_create.html', title='Create Blog Post', form=form)

@blog_bp.route('/blog/edit/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Blog.get_post(mongo, post_id)
    
    if not post:
        abort(404)
    
    # Check if user is the author or an admin
    if post['author_id'] != ObjectId(current_user.get_id()) and not current_user.is_admin:
        abort(403)
    
    form = BlogPostForm()
    
    if form.validate_on_submit():
        # Handle image update
        if form.image.data:
            image_filename = save_blog_image(form.image.data)
        else:
            image_filename = post.get('image')
        
        # Process tags
        tags = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
        
        # Update blog post
        Blog.update_post(
            mongo,
            post_id=post_id,
            title=form.title.data,
            content=form.content.data,
            image_filename=image_filename,
            tags=tags,
            status=form.status.data
        )
        
        flash('Your blog post has been updated!', 'success')
        return redirect(url_for('blog.blog_detail', post_id=post_id))
    
    elif request.method == 'GET':
        # Prefill form with post data
        form.title.data = post['title']
        form.content.data = post['content']
        form.status.data = post['status']
        form.tags.data = ', '.join(post.get('tags', []))
    
    return render_template(
        'blog/blog_edit.html',
        title='Edit Blog Post',
        form=form,
        post=post
    )

@blog_bp.route('/blog/delete/<post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Blog.get_post(mongo, post_id)
    
    if not post:
        abort(404)
    
    # Check if user is the author or an admin
    if post['author_id'] != ObjectId(current_user.get_id()) and not current_user.is_admin:
        abort(403)
    
    # Delete blog post
    Blog.delete_post(mongo, post_id)
    
    flash('Your blog post has been deleted!', 'success')
    return redirect(url_for('blog.blog_list'))

@blog_bp.route('/blog/tag/<tag>')
def posts_by_tag(tag):
    page = request.args.get('page', 1, type=int)
    per_page = 6
    skip = (page - 1) * per_page
    
    # Count posts with this tag
    total_posts = mongo.db.blog_posts.count_documents({
        'tags': tag,
        'status': 'published'
    })
    
    total_pages = (total_posts + per_page - 1) // per_page
    
    # Get posts with this tag
    posts = list(mongo.db.blog_posts.find({
        'tags': tag,
        'status': 'published'
    }).sort('created_at', -1).skip(skip).limit(per_page))
    
    # Get all tags for sidebar
    all_tags = mongo.db.blog_posts.distinct('tags')
    
    # Get recent posts for sidebar
    recent_posts = Blog.get_all_posts(mongo, limit=3)
    
    return render_template(
        'blog/blog_list.html',
        title=f'Posts tagged with "{tag}" | EduFuture',
        posts=posts,
        page=page,
        total_pages=total_pages,
        current_tag=tag,
        tags=all_tags,
        recent_posts=recent_posts
    )

@blog_bp.route('/blog/like/<post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    # Toggle like status
    Blog.toggle_like(mongo, post_id, current_user.get_id())
    
    # Return to previous page
    return redirect(request.referrer or url_for('blog.blog_detail', post_id=post_id))

@blog_bp.route('/blog/author/<author_id>')
def author_posts(author_id):
    # Get author info
    author = mongo.db.users.find_one({'_id': ObjectId(author_id)})
    if not author:
        abort(404)
    
    # Get posts by this author
    posts = Blog.get_posts_by_author(mongo, author_id, status='published')
    
    return render_template(
        'blog/author_posts.html',
        title=f'Posts by {author["username"]} | EduFuture',
        author=author,
        posts=posts
    )

@blog_bp.route('/my-posts')
@login_required
def my_posts():
    # Get all posts by current user
    posts = Blog.get_posts_by_author(mongo, current_user.get_id())
    
    return render_template(
        'blog/my_posts.html',
        title='My Blog Posts | EduFuture',
        posts=posts
    ) 