from flask import Flask
from extensions import db, login_manager
from routes import register_routes

app = Flask(__name__)
app.secret_key = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# Register routes
register_routes(app)
print(app.url_map)

if __name__ == '__main__':
    with app.app_context():
        from models import create_default_user
        create_default_user()
    app.run(debug=True)
