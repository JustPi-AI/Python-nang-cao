from datetime import datetime
from extensions import db
from flask_login import UserMixin

# User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    real_name = db.Column(db.String(120), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    about_me = db.Column(db.Text, nullable=True)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime)
    avatar = db.Column(db.String(255), default='static/watermelon.gif')

    def __repr__(self):
        return f'<User {self.username}>'

# Create default user (used in app.py)
def create_default_user():
    db.create_all()
    default_user = User.query.filter_by(username='duyphuc').first()
    if not default_user:
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash('123', method='pbkdf2:sha256')
        new_user = User(
            username='duyphuc',
            email='phuc.2174802010361@vanlanguni.vn',
            password=hashed_password,
            avatar='static/watermelon.gif'
        )
        db.session.add(new_user)
        db.session.commit()
