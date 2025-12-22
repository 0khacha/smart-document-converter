from flask import Flask
from config import Config
import os

def create_app():
    """Application factory pattern"""
    # Get the parent directory (project root)
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(Config)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app