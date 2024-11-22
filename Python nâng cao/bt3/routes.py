from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from extensions import login_manager
from utils import allowed_file
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# Hàm để Flask-Login tải thông tin người dùng từ cơ sở dữ liệu
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))

def register_routes(app):
    # Default route
    @app.route('/')
    def index():
        return redirect(url_for('home'))

    # Home route
    @app.route('/home')
    def home():
        return render_template('home.html')

    # Login route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                user.last_seen = datetime.utcnow()
                db.session.commit()
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Login failed. Check your username and password.')
        return render_template('login.html')

    # Logout route
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    # Registration route
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                flash('Passwords do not match!')
                return redirect(url_for('register'))

            if User.query.filter_by(email=email).first():
                flash('Email is already registered! Please use a different email.')
                return redirect(url_for('register'))

            if User.query.filter_by(username=username).first():
                flash('Username is already taken! Please choose a different username.')
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(email=email, username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('You have successfully registered!')
            return redirect(url_for('login'))

        return render_template('register.html')

    # Profile route
    @app.route('/profile')
    @login_required
    def profile():
        return render_template(
            'profile.html',
            username=current_user.username,
            email=current_user.email,
            real_name=current_user.real_name,
            location=current_user.location,
            about_me=current_user.about_me,
            member_since=current_user.member_since.strftime("%B %d, %Y"),
            last_seen=current_user.last_seen.strftime("%B %d, %Y %I:%M %p") if current_user.last_seen else "Never",
            avatar=current_user.avatar
        )

    # Edit Profile route
    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        if request.method == 'POST':
            current_user.real_name = request.form['real_name']
            current_user.location = request.form['location']
            current_user.about_me = request.form['about_me']
            avatar = request.files.get('avatar')

            if avatar and allowed_file(avatar.filename):
                filename = secure_filename(avatar.filename)
                avatar_path = os.path.join('static', filename)
                avatar.save(avatar_path)
                current_user.avatar = f'{filename}'

            db.session.commit()
            flash('Your profile has been updated!')
            return redirect(url_for('profile'))

        return render_template(
            'edit_profile.html',
            username=current_user.username,
            real_name=current_user.real_name,
            location=current_user.location,
            about_me=current_user.about_me
        )
    