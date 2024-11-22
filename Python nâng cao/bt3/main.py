from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.utils import secure_filename
import os 

app = Flask(__name__)
app.secret_key = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Route mặc định, tự động chuyển hướng tới /home
@app.route('/')
def index():
    return redirect(url_for('home'))

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    real_name = db.Column(db.String(120), nullable=True)  
    location = db.Column(db.String(120), nullable=True)    
    about_me = db.Column(db.Text, nullable=True)           
    member_since = db.Column(db.DateTime, default=datetime.utcnow)  
    last_seen = db.Column(db.DateTime)  
    avatar = db.Column(db.String(255), default='static/watermelon.gif')  # Default avatar

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def follower_count(self):
        return Follow.query.filter_by(followed_id=self.id).count()

    @property
    def following_count(self):
        return Follow.query.filter_by(follower_id=self.id).count()

    def is_following(self, user):
        return Follow.query.filter_by(follower_id=self.id, followed_id=user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            follow_record = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow_record)
            db.session.commit()

    def unfollow(self, user):
        follow_record = Follow.query.filter_by(follower_id=self.id, followed_id=user.id).first()
        if follow_record:
            db.session.delete(follow_record)
            db.session.commit()

# BlogPost model
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Add this line
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Define a relationship to link the post to a user
    user = db.relationship('User', backref='posts')  # Optional for easy access to the user's posts

# Follow model
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    follower = db.relationship('User', foreign_keys=[follower_id], backref='following')  # backref for who a user is following
    followed = db.relationship('User', foreign_keys=[followed_id], backref='followers')  # backref for who is following the user

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create default user and blog table
def create_default_user():
    db.create_all()
    default_user = User.query.filter_by(username='duyphuc').first()
    if not default_user:
        hashed_password = generate_password_hash('123', method='pbkdf2:sha256') # Phương pháp mã hóa=''
        new_user = User(username='duyphuc', 
                        email='phuc.2174802010361@vanlanguni.vn',  
                        password=hashed_password,
                        avatar='static/watermelon.gif')  # Set the avatar 

        db.session.add(new_user)
        db.session.commit()

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            user.last_seen = datetime.utcnow()  # Update last seen time
            db.session.commit()
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your username and password.')
    return render_template('login.html')

# Route for profile page
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', 
                           username=current_user.username, 
                           email=current_user.email,
                           real_name=current_user.real_name,
                           location=current_user.location,
                           about_me=current_user.about_me,
                           member_since=current_user.member_since.strftime("%B %d, %Y"),
                           last_seen=current_user.last_seen.strftime("%B %d, %Y %I:%M %p") if current_user.last_seen else "Never",
                           avatar=current_user.avatar)

# Blog route with pagination
@app.route('/blog', methods=['GET', 'POST'])
@login_required
def blog():
    if request.method == 'POST':
        # Check if the user is authenticated before proceeding
        if not current_user.is_authenticated:
            flash('You must be logged in to create a post.')
            return redirect(url_for('login'))

        title = request.form['title']
        content = request.form['content']
        new_post = BlogPost(title=title, content=content, user_id=current_user.id)  # Add user_id here
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!')
        return redirect(url_for('blog'))

    page = request.args.get('page', 1, type=int)  # Get current page number
    per_page = 2  # Number of posts per page
    posts = BlogPost.query.order_by(BlogPost.timestamp.desc()).paginate(page=page, per_page=per_page)  # Pagination
    return render_template('blog.html', posts=posts)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for editing profile
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.real_name = request.form['real_name']
        current_user.location = request.form['location']
        current_user.about_me = request.form['about_me']
        avatar = request.files.get('avatar')  # Lấy file avatar nếu có
        
        # Xử lý file avatar nếu có
        if avatar and allowed_file(avatar.filename):
            filename = secure_filename(avatar.filename)
            avatar_path = os.path.join('static/', filename)

            # Lưu avatar vào thư mục tĩnh
            avatar.save(avatar_path)

            # Cập nhật avatar trong cơ sở dữ liệu
            current_user.avatar = f'{filename}'
        db.session.commit()
        flash('Your profile has been updated!')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', 
                           username=current_user.username,
                           real_name=current_user.real_name,
                           location=current_user.location,
                           about_me=current_user.about_me)

# Route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route for user registration
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
        new_user = User(email=email, username=username, password=hashed_password, avatar='janedoe.gif')
        db.session.add(new_user)
        db.session.commit()
        flash('You have successfully registered!')
        return redirect(url_for('login'))

    return render_template('register.html')

# Route for unconfirmed page
@app.route('/unconfirmed')
@login_required
def unconfirmed():
    return render_template('unconfirmed.html', username=current_user.username if current_user.is_authenticated else 'Guest')

# Route for user profile page with follow/unfollow functionality
@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    following = current_user.is_following(user)  # Kiểm tra người dùng hiện tại có theo dõi không
    followed_by = user.is_following(current_user)  # Kiểm tra người dùng này có theo dõi người dùng hiện tại không
    
    if request.method == 'POST':
        if following:
            current_user.unfollow(user)
        else:
            current_user.follow(user)

        return redirect(url_for('user_profile', username=username))  # Điều hướng lại trang profile sau khi hành động

    return render_template('user_profile.html', user=user, following=following, followed_by=followed_by)


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)  # Fetch the blog post or return a 404 if not found

    # Check if the current user is the author of the post
    if post.user_id != current_user.id:
        flash('You do not have permission to edit this post.')
        return redirect(url_for('blog'))  # Redirect to the blog page if not authorized

    if request.method == 'POST':
        post.title = request.form['title']  # Update the post title
        post.content = request.form['content']  # Update the post content
        db.session.commit()  # Save changes to the database
        flash('Your post has been updated!')
        return redirect(url_for('blog'))  # Redirect back to the blog page

    return render_template('edit_post.html', post=post)  # Render edit form with current post data

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user_to_follow = User.query.get_or_404(user_id)
    if not current_user.is_following(user_to_follow):
        new_follow = Follow(follower_id=current_user.id, followed_id=user_to_follow.id)
        db.session.add(new_follow)
        db.session.commit()
        flash(f'You are now following {user_to_follow.username}!')
    else:
        flash(f'You are already following {user_to_follow.username}.')
    return redirect(url_for('user_profile', username=user_to_follow.username))

@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    user_to_unfollow = User.query.get_or_404(user_id)
    follow_record = Follow.query.filter_by(follower_id=current_user.id, followed_id=user_to_unfollow.id).first()
    if follow_record:
        db.session.delete(follow_record)
        db.session.commit()
        flash(f'You have unfollowed {user_to_unfollow.username}.')
    return redirect(url_for('user_profile', username=user_to_unfollow.username))


@app.route('/followed')
@login_required
def followed():
    # Get the IDs of users that the current user is following
    followed_user_ids = [followed.followed_id for followed in Follow.query.filter_by(follower_id=current_user.id).all()]
    
    # Paginate posts by followed users
    page = request.args.get('page', 1, type=int)  # Get current page number
    per_page = 2  # Number of posts per page
    posts = BlogPost.query.filter(BlogPost.user_id.in_(followed_user_ids)).order_by(BlogPost.timestamp.desc()).paginate(page=page, per_page=per_page)
    
    return render_template('blog.html', posts=posts)

# Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    enabled = db.Column(db.Boolean, default=True)  # Add this attribute
    approved = db.Column(db.Boolean, default=False)  # New field for moderation status

    post = db.relationship('BlogPost', backref='comments')
    user = db.relationship('User')

@app.route('/moderate')
@login_required
def moderate():
    # Retrieve comments that are not approved yet
    comments_to_moderate = Comment.query.filter_by(approved=False).all()
    return render_template('moderate.html', comments_to_moderate=comments_to_moderate)

@app.route('/approve_comment/<int:comment_id>', methods=['POST'])
@login_required
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.approved = True
    db.session.commit()
    flash('Comment approved.')
    return redirect(url_for('moderate'))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.')
    return redirect(url_for('moderate'))


@app.route('/moderate_comment/<int:comment_id>', methods=['POST'])
@login_required
def moderate_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.enabled = not comment.enabled  # Toggle the enabled status
    db.session.commit()
    flash('Comment visibility updated.')
    return redirect(url_for('comments', post_id=comment.post_id))

@app.route('/post/<int:post_id>/comments', methods=['GET', 'POST'])
@login_required
def comments(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if request.method == 'POST':
        content = request.form['content']
        new_comment = Comment(content=content, post_id=post.id, user_id=current_user.id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Your comment has been added and is awaiting approval.')
        return redirect(url_for('comments', post_id=post.id))
    
    # Pagination for comments
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Number of comments per page
    # Display only approved comments
    comments = Comment.query.filter_by(post_id=post.id, approved=False).order_by(Comment.timestamp.desc()).paginate(page=page, per_page=per_page)
    return render_template('comments.html', post=post, comments=comments)

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

# Sample data structure for storing registrations (modify with database queries as needed)
registrations = []

@app.route('/dangkyhocphan', methods=['GET', 'POST'])
@login_required
def dangkyhocphan():
    if request.method == 'POST':
        course_id = request.form.get('course_id')

        # Simulate fetching course details (replace with database lookup)
        course_details = {
            '232_71ITAI41303_01': {'name': 'Các công cụ và nền tảng cho trí tuệ nhân tạo', 'credits': 3},
            '232_71ITIS30303_01': {'name': 'Quản lý Dự án công nghệ thông tin', 'credits': 3},
            '222_71ITAI40803_01': {'name': 'Nhập môn xử lý ảnh số', 'credits': 3},
            '223_71ITAI40503_01': {'name': 'Trí tuệ nhân tạo ứng dụng', 'credits': 3},
            '211_71ITBS10203_03': {'name': 'Cơ sở lập trình (DKHP_WIN)', 'credits': 3},
            '211_71ITBS10103_05': {'name': 'Nhập môn Công nghệ thông tin (DKHP_WIN)', 'credits': 3},
            '221_71ITSE30203_01': {'name': 'Lập trình hướng đối tượng', 'credits': 3},
            '221_71ITSE30303_01': {'name': 'Cấu trúc dữ liệu và giải thuật', 'credits': 3},
            '222_71ITDS40203_01': {'name': 'Xác suất thống kê ứng dụng', 'credits': 3},
        }

        if course_id in course_details:
            # Check if already registered
            if course_id not in [reg['code'] for reg in registrations if reg['user_id'] == current_user.id]:
                registrations.append({
                    'user_id': current_user.id,
                    'code': course_id,
                    'name': course_details[course_id]['name'],
                    'credits': course_details[course_id]['credits'],
                })
                flash('Môn học đã được đăng ký thành công!', 'success')
            else:
                flash('Bạn đã đăng ký môn học này.', 'warning')
        else:
            flash('Mã học phần không hợp lệ.', 'error')

        return redirect(url_for('dangkyhocphan'))

    return render_template('dangkyhocphan.html', registrations=[reg for reg in registrations if reg['user_id'] == current_user.id])


# Course model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Course {self.name}>'

# CourseRegistration model (for user-course relationship)
class CourseRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='courses')
    course = db.relationship('Course', backref='registrations')

    def __repr__(self):
        return f'<Registration {self.user.username} -> {self.course.name}>'

# Route để xem các môn học có thể đăng ký
@app.route('/courses', methods=['GET'])
@login_required
def courses():
    courses = Course.query.all()  # Lấy tất cả các môn học
    return render_template('courses.html', courses=courses)

# Route để đăng ký môn học
@app.route('/register_course/<int:course_id>', methods=['POST'])
@login_required
def register_course(course_id):
    course = Course.query.get_or_404(course_id)
    existing_registration = CourseRegistration.query.filter_by(user_id=current_user.id, course_id=course.id).first()

    if existing_registration:
        flash('Bạn đã đăng ký môn học này rồi!', 'danger')
    else:
        registration = CourseRegistration(user_id=current_user.id, course_id=course.id)
        db.session.add(registration)
        db.session.commit()
        flash('Đăng ký môn học thành công!', 'success')

    return redirect(url_for('courses'))

@app.route('/huydangkyhocphan', methods=['POST'])
@login_required
def huydangkyhocphan():
    course_id = request.form.get('course_id')
    
    # Remove the course from registrations
    global registrations
    registrations = [reg for reg in registrations if reg['code'] != course_id]

    flash('Hủy đăng ký môn học thành công!', 'success')
    return redirect(url_for('dangkyhocphan'))


@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    with app.app_context():
        create_default_user()  # Create default user if not exists
    app.run(debug=True)

