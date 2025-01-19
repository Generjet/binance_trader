from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from apps import db
from apps.blog.forms import BlogPostForm
from apps.models import BlogPost
from werkzeug.utils import secure_filename
import os
blog_bp = Blueprint('blog', __name__, url_prefix='/blog')

@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = BlogPostForm()
    if form.validate_on_submit():
        # Handle file upload
        thumbnail = None
        if form.thumbnail.data:
            filename = secure_filename(form.thumbnail.data.filename)
            filepath = os.path.join('apps/static/uploads/blog', filename)
            form.thumbnail.data.save(filepath)
            thumbnail = f'static/uploads/blog/{filename}'

        # Extract plain text from content
        import re
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(form.content.data, 'html.parser')
        content_text = soup.get_text()
        
        # Create new blog post
        post = BlogPost(
            title=form.title.data,
            content=form.content.data,
            content_text=content_text,
            author_id=current_user.id,
            category=form.category.data,
            thumbnail=thumbnail
        )
        
        try:
            db.session.add(post)
            db.session.commit()
            flash('Blog post created successfully!', 'success')
            return redirect(url_for('blog.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating post: {str(e)}', 'danger')
            return redirect(url_for('blog.index'))

    return render_template('blog/create_post.html', form=form)

@blog_bp.route('/post/<int:post_id>')
def view_post(post_id):
    post = BlogPost.find_by_id(post_id)
    if not post:
        flash('Post not found', 'danger')
        return redirect(url_for('blog.index'))
    return render_template('blog/view_post.html', post=post)

@blog_bp.route('/')
def index():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('blog/index.html', posts=posts)

@blog_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = BlogPost.find_by_id(post_id)
    if not post or post.author_id != current_user.id:
        flash('Post not found or unauthorized', 'danger')
        return redirect(url_for('blog.index'))

    form = BlogPostForm(obj=post)
    if form.validate_on_submit():
        # Handle file upload
        if form.thumbnail.data and hasattr(form.thumbnail.data, 'filename'):
            filename = secure_filename(form.thumbnail.data.filename)
            filepath = os.path.join('apps/static/uploads/blog', filename)
            form.thumbnail.data.save(filepath)
            post.thumbnail = f'static/uploads/blog/{filename}'
        elif request.form.get('remove_thumbnail'):
            post.thumbnail = None

        # Extract plain text from content
        import re
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(form.content.data, 'html.parser')
        post.content_text = soup.get_text()
        
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        
        try:
            db.session.commit()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('blog.view_post', post_id=post.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating post: {str(e)}', 'danger')

    return render_template('blog/edit_post.html', form=form, post=post)

@blog_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = BlogPost.find_by_id(post_id)
    if not post or post.author_id != current_user.id:
        flash('Post not found or unauthorized', 'danger')
        return redirect(url_for('blog.index'))

    try:
        post.delete()
        flash('Post deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting post: {str(e)}', 'danger')
    
    return redirect(url_for('blog.index'))
