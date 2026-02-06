#!/usr/bin/env python3
"""
AI Voice Assistant Pro - Main Application Entry Point

This is the main entry point for the AI Voice Assistant Pro application.
It initializes the Flask app and starts the voice assistant service.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from voice_chatbot.core.app import VoiceChatbot
from voice_chatbot.core.config import Config
from flask import Flask
from flask_cors import CORS
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/voice_chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
           template_folder='web/templates',
           static_folder='web/static')
CORS(app)

# Configure Flask
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.getenv('FLASK_ENV') == 'development'

# Initialize voice chatbot
try:
    chatbot = VoiceChatbot()
    logger.info("✅ AI Voice Assistant Pro initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize voice chatbot: {e}")
    sys.exit(1)

# Import and register API routes
from voice_chatbot.api.routes import register_routes
register_routes(app, chatbot)

if __name__ == '__main__':
    port = Config.PORT
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"🚀 Starting AI Voice Assistant Pro on {host}:{port}")
    logger.info(f"🌐 Web Interface: http://{host}:{port}")
    logger.info(f"📊 API Status: http://{host}:{port}/api/status")
    
    try:
        app.run(host=host, port=port, debug=app.config['DEBUG'])
    except KeyboardInterrupt:
        logger.info("👋 Shutting down AI Voice Assistant Pro...")
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        sys.exit(1)
