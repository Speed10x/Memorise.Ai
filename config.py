import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '5223903292'))
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'reminder_bot')

# Subscription Plans
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Free Plan',
        'max_reminders': 5,
        'max_daily_reminders': 3,
        'price': 0
    },
    'premium': {
        'name': 'Premium Plan',
        'max_reminders': 100,
        'max_daily_reminders': 50,
        'price': 9.99
    },
    'unlimited': {
        'name': 'Unlimited Plan',
        'max_reminders': -1,  # -1 means unlimited
        'max_daily_reminders': -1,
        'price': 19.99
    }
}

# Bot Settings
TIMEZONE = os.getenv('TIMEZONE', 'UTC')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Webhook Configuration (for Koyeb deployment)
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = int(os.getenv('PORT', 8000))
