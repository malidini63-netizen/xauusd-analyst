from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

TWELVEDATA_API_KEY = os.getenv('TWELVEDATA_API_KEY')
GROQ_API_KEY       = os.getenv('GROQ_API_KEY')
AI_MODEL           = os.getenv('AI_MODEL')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID   = os.getenv('TELEGRAM_CHAT_ID')

SYMBOL = 'XAU/USD'
TIMEFRAMES = {'H4': '4h', 'H1': '1h', 'M15': '15min', 'M5': '5min'}

def assert_config():
    missing = [k for k, v in {'GROQ_API_KEY': GROQ_API_KEY, 'AI_MODEL': AI_MODEL}.items() if not v]
    if missing:
        raise RuntimeError(f'Variables manquantes : {missing}')
