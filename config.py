import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Telegram Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_API_ID = os.getenv('BOT_API_ID')
BOT_API_HASH = os.getenv('BOT_API_HASH')

# Admin Configuration
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-secret-key')

# Database Configuration
DATABASE_PATH = BASE_DIR / os.getenv('DATABASE_PATH', 'database/bot.db')

# Web Admin Configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Session Storage
SESSION_DIR = BASE_DIR / os.getenv('SESSION_DIR', 'sessions')

# Default Settings
DEFAULT_CONFIRMATION_TIME = int(os.getenv('DEFAULT_CONFIRMATION_TIME', 5))
MIN_WITHDRAW_BALANCE = float(os.getenv('MIN_WITHDRAW_BALANCE', 10))
MAX_WITHDRAW_BALANCE = float(os.getenv('MAX_WITHDRAW_BALANCE', 10000))

# Ensure directories exist
SESSION_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
