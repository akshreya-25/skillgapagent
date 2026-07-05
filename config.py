import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'skill-gap-analysis-agent-super-secret-key-12345')
    
    # Path configurations
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASE_DIR, 'database.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    
    # File upload configurations
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    
    # Gemini API Key configuration
    GEMINI_API_KEY = "AQ.Ab8RN6J9om5HUQORA_jKc7ptkVhEJeaHdogQPVDjngp77Ewhwg"

# Create directories if they do not exist
os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads'), exist_ok=True)
os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'images'), exist_ok=True)
os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'css'), exist_ok=True)
os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'js'), exist_ok=True)
os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates'), exist_ok=True)
os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'docs'), exist_ok=True)
