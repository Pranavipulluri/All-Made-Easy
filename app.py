from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import requests

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile_pic = db.Column(db.String(200), default='default_profile.jpg')
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image_filename = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('contents', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

class Bike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    availability_status = db.Column(db.String(50), default='Available')
    available_in = db.Column(db.Integer, default=0)
    image_filename = db.Column(db.String(120), default='default_bike.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('bikes', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Incomplete')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    salary_range = db.Column(db.String(100))
    contact_email = db.Column(db.String(100), nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('jobs', lazy=True))

# API configuration
API_KEY = '680e232fbbab48cd8a633909d3ced6eb'
NEWS_API_URL = 'https://newsapi.org/v2/top-headlines'

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(route_function):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return route_function(*args, **kwargs)
    wrapper.__name__ = route_function.__name__
    return wrapper

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    user = User.query.get(session['user_id'])
    contents = Content.query.order_by(Content.created_at.desc()).limit(5).all()
    bikes = Bike.query.filter_by(availability_status='Available').limit(3).all()
    tasks = Task.query.filter_by(user_id=session['user_id']).order_by(Task.due_date).limit(3).all()
    
    return render_template('home.html', 
                          user=user, 
                          contents=contents, 
                          bikes=bikes, 
                          tasks=tasks)


@app.context_processor
def inject_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        # Check if user has profile_pic attribute
        if user and not hasattr(user, 'profile_pic'):
            user.profile_pic = 'default_profile.jpg'
        return {'current_user': user}
    return {'current_user': None}


# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:  # In production, use proper password hashing
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            flash('Username already exists', 'error')
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully', 'success')
            return redirect(url_for('login'))
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Profile routes
@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    contents = Content.query.filter_by(user_id=session['user_id']).all()
    bikes = Bike.query.filter_by(user_id=session['user_id']).all()
    return render_template('profile.html', user=user, contents=contents, bikes=bikes)


@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get(session['user_id'])
    
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.profile_pic = filename
    
    if request.form.get('new_password') and request.form.get('current_password'):
        if user.password == request.form.get('current_password'):
            user.password = request.form.get('new_password')
        else:
            flash('Current password is incorrect', 'error')
            return redirect(url_for('profile'))
    
    db.session.commit()
    flash('Profile updated successfully', 'success')
    return redirect(url_for('profile'))

# Content sharing routes
@app.route('/content')
@login_required
def content_sharing():
    contents = Content.query.order_by(Content.created_at.desc()).all()
    return render_template('content_sharing.html', contents=contents)

@app.route('/community_content')
def community_content():
    # Fetch all content from the database
    contents = Content.query.all()
    return render_template('community_content.html', contents=contents)

# Share content route
@app.route('/content/share', methods=['POST'])
@login_required
def share_content():
    content_id = request.form.get('content_id')
    receiver_id = request.form.get('receiver_id')

    content = Content.query.get(content_id)
    receiver = User.query.get(receiver_id)

    if content and receiver:
        # Create a new message to share the content
        new_message = Message(
            sender_id=session['user_id'],
            receiver_id=receiver_id,
            content=f"Check out this content: {content.title} - {content.description}"
        )
        db.session.add(new_message)
        db.session.commit()
        flash('Content shared successfully', 'success')
    else:
        flash('Content or receiver not found', 'error')

    return redirect(url_for('content_sharing'))


@app.route('/content/my')
@login_required
def my_content():
    user_id = session['user_id']
    contents = Content.query.filter_by(user_id=user_id).order_by(Content.created_at.desc()).all()
    return render_template('my_content.html', contents=contents)

@app.route('/edit_bike/<int:bike_id>', methods=['GET', 'POST'])
@login_required
def edit_bike(bike_id):
    bike = Bike.query.get(bike_id)
    if bike and bike.user_id == session['user_id']:
        if request.method == 'POST':
            bike.name = request.form.get('bike_name')
            bike.condition = request.form.get('condition')
            bike.price_per_hour = float(request.form.get('price_per_hour'))

            file = request.files.get('bike_image')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                bike.image_filename = filename

            db.session.commit()
            flash('Bike details updated successfully', 'success')
            return redirect(url_for('bike_sharing'))

        return render_template('edit_bike.html', bike=bike)
    else:
        flash('Bike not found or not authorized', 'error')
        return redirect(url_for('bike_sharing'))


@app.route('/content/add', methods=['GET', 'POST'])
@login_required
def add_content():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('image')
        
        if not (title and description and file and allowed_file(file.filename)):
            flash('Please provide all required information and a valid image file', 'error')
            return redirect(url_for('add_content'))
            
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        new_content = Content(
            title=title,
            description=description,
            image_filename=filename,
            user_id=session['user_id']
        )
        
        db.session.add(new_content)
        db.session.commit()
        flash('Content added successfully', 'success')
        return redirect(url_for('content_sharing'))
        
    return render_template('add_content.html')

@app.route('/content/delete/<int:content_id>', methods=['POST'])
@login_required
def delete_content(content_id):
    content = Content.query.get(content_id)
    if content and content.user_id == session['user_id']:
        db.session.delete(content)
        db.session.commit()
        flash('Content deleted successfully', 'success')
    else:
        flash('Content not found or not authorized', 'error')
    return redirect(url_for('my_content'))

# Bike sharing routes
@app.route('/bike_sharing')
@login_required
def bike_sharing():
    bikes = Bike.query.all()
    user_bikes = Bike.query.filter_by(user_id=session['user_id']).all()
    return render_template('bike_sharing.html', bikes=bikes, user_bikes=user_bikes)

@app.route('/add_bike', methods=['GET', 'POST'])
@login_required
def add_bike():
    if request.method == 'POST':
        bike_name = request.form.get('bike_name')
        condition = request.form.get('condition')
        price_per_hour = request.form.get('price_per_hour')
        
        file = request.files.get('bike_image')
        filename = 'default_bike.jpg'
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_bike = Bike(
            name=bike_name,
            condition=condition,
            price_per_hour=float(price_per_hour),
            image_filename=filename,
            user_id=session['user_id'],
            availability_status='Available'
        )
        
        db.session.add(new_bike)
        db.session.commit()
        flash('Bike added successfully', 'success')
        return redirect(url_for('bike_sharing'))
        
    return render_template('add_bike.html')

@app.route('/delete_bike/<int:bike_id>', methods=['POST'])
@login_required
def delete_bike(bike_id):
    bike = Bike.query.get(bike_id)
    if bike and bike.user_id == session['user_id']:
        db.session.delete(bike)
        db.session.commit()
        flash('Bike deleted successfully', 'success')
    else:
        flash('Bike not found or not authorized', 'error')
    return redirect(url_for('bike_sharing'))

@app.route('/rent_bike/<int:bike_id>', methods=['POST'])
@login_required
def rent_bike(bike_id):
    bike = Bike.query.get(bike_id)
    if bike and bike.availability_status == 'Available':
        rental_hours = int(request.form.get('rental_hours', 1))
        bike.availability_status = 'Rented'
        bike.available_in = rental_hours
        db.session.commit()
        flash(f'You have rented {bike.name} for {rental_hours} hours', 'success')
    else:
        flash('Bike is not available for rent', 'error')
    return redirect(url_for('bike_sharing'))

# To-do list routes
@app.route('/todo')
@login_required
def todo():
    category_filter = request.args.get('filter', 'all')
    user_id = session['user_id']
    
    # Update missed tasks
    now = datetime.now().date()
    tasks_to_update = Task.query.filter(
        Task.user_id == user_id,
        Task.due_date < now,
        Task.status == 'Incomplete'
    ).all()
    
    for task in tasks_to_update:
        task.status = 'Missed'
    
    if tasks_to_update:
        db.session.commit()
    
    # Filter tasks
    if category_filter == 'all':
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.due_date).all()
    else:
        tasks = Task.query.filter_by(
            user_id=user_id, 
            category=category_filter
        ).order_by(Task.due_date).all()
    
    categories = db.session.query(Task.category).filter_by(user_id=user_id).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('todo.html', 
                          tasks=tasks, 
                          categories=categories, 
                          category_filter=category_filter)

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    task_name = request.form.get('task_name')
    due_date = request.form.get('due_date')
    category = request.form.get('category')
    
    if not (task_name and due_date and category):
        flash('Please provide all task information', 'error')
        return redirect(url_for('todo'))
        
    try:
        due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
        
        if due_date_obj < datetime.now().date():
            flash('Cannot set a past date!', 'error')
            return redirect(url_for('todo'))
            
        new_task = Task(
            name=task_name,
            due_date=due_date_obj,
            category=category,
            status='Incomplete',
            user_id=session['user_id']
        )
        
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully', 'success')
    except Exception as e:
        flash(f'Error adding task: {str(e)}', 'error')
        
    return redirect(url_for('todo'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == session['user_id']:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully', 'success')
    else:
        flash('Task not found or not authorized', 'error')
    return redirect(url_for('todo'))

@app.route('/update_task_status/<int:task_id>', methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == session['user_id']:
        task.status = request.form.get('status', 'Incomplete')
        db.session.commit()
        flash('Task status updated', 'success')
    else:
        flash('Task not found or not authorized', 'error')
    return redirect(url_for('todo'))

# Chat routes
@app.route('/chat')
@login_required
def chat_list():
    user_id = session['user_id']
    
    # Find all users who have chatted with the current user
    chat_partners = db.session.query(User).join(
        Message, 
        ((Message.sender_id == User.id) & (Message.receiver_id == user_id)) | 
        ((Message.receiver_id == User.id) & (Message.sender_id == user_id))
    ).filter(User.id != user_id).distinct().all()
    
    # Get all users for starting new chats
    all_users = User.query.filter(User.id != user_id).all()
    
    return render_template('chat_list.html', chat_partners=chat_partners, all_users=all_users)

@app.route('/chat/<int:receiver_id>')
@login_required
def chat(receiver_id):
    sender_id = session['user_id']
    receiver = User.query.get(receiver_id)
    
    if not receiver:
        flash('User not found', 'error')
        return redirect(url_for('chat_list'))
    
    # Mark messages as read
    unread_messages = Message.query.filter_by(
        sender_id=receiver_id, 
        receiver_id=sender_id,
        is_read=False
    ).all()
    
    for msg in unread_messages:
        msg.is_read = True
    
    if unread_messages:
        db.session.commit()
    
    # Get all messages between the two users
    messages = Message.query.filter(
        ((Message.sender_id == sender_id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == sender_id))
    ).order_by(Message.timestamp).all()
    
    return render_template('chat.html', messages=messages, receiver=receiver)

@app.route('/chat/send', methods=['POST'])
@login_required
def send_message():
    sender_id = session['user_id']
    receiver_id = request.form.get('receiver_id')
    content = request.form.get('content')
    
    if not content or not content.strip():
        flash('Cannot send empty message', 'error')
        return redirect(url_for('chat', receiver_id=receiver_id))
    
    new_message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    return redirect(url_for('chat', receiver_id=receiver_id))

# Job board routes
@app.route('/job_board')
@login_required
def job_board():
    jobs = Job.query.order_by(Job.posted_at.desc()).all()
    return render_template('job_board.html', jobs=jobs)

@app.route('/post_job', methods=['GET', 'POST'])
@login_required
def post_job():
    if request.method == 'POST':
        title = request.form.get('title')
        company = request.form.get('company')
        location = request.form.get('location')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        salary_range = request.form.get('salary_range')
        contact_email = request.form.get('contact_email')
        
        if not all([title, company, location, description, requirements, contact_email]):
            flash('Please fill all required fields', 'error')
            return redirect(url_for('post_job'))
        
        new_job = Job(
            title=title,
            company=company,
            location=location,
            description=description,
            requirements=requirements,
            salary_range=salary_range,
            contact_email=contact_email,
            posted_by=session['user_id']
        )
        
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully', 'success')
        return redirect(url_for('job_board'))
        
    return render_template('post_job.html')

@app.route('/delete_job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    job = Job.query.get(job_id)
    if job and job.posted_by == session['user_id']:
        db.session.delete(job)
        db.session.commit()
        flash('Job deleted successfully', 'success')
    else:
        flash('Job not found or not authorized', 'error')
    return redirect(url_for('job_board'))

# News routes
@app.route('/tech_news')
@login_required
def tech_news():
    try:
        params = {
            'category': 'technology',
            'apiKey': API_KEY,
            'language': 'en',
            'pageSize': 10
        }
        response = requests.get(NEWS_API_URL, params=params)
        news_data = response.json()
        
        if news_data.get('status') == 'ok':
            articles = news_data.get('articles', [])
            return render_template('tech_news.html', articles=articles)
        else:
            flash('Failed to fetch news', 'error')
            return render_template('tech_news.html', articles=[])
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('tech_news.html', articles=[])

# Learning center routes
@app.route('/learning_center')
@login_required
def learning_center():
    return render_template('learning_center.html')

# Community routes
@app.route('/community')
@login_required
def community():
    users = User.query.filter(User.id != session['user_id']).all()
    return render_template('community.html', users=users)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Server error'), 500


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)