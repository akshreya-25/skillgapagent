import os
from flask import Flask
from flask_login import LoginManager

from config import Config
from database import init_db
from models import User
from routes import main_bp

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize Database
    with app.app_context():
        init_db()
        print("Database initialized successfully.")
        
    # Configure Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(int(user_id))
        
    # Register blueprints
    app.register_blueprint(main_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    # Run the Flask app on localhost, port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
