import os

# Base paths (work both locally and in container)
_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(_CONFIG_DIR)

# Telegram settings
TELEGRAM_BOT_TOKEN = "8525211549:AAEVGEuJDTrGz64UXm2gaoWqfnsKuPBg234"
ADMIN_ID = 866418979

# Level.Travel API settings
LEVEL_TRAVEL_API_URL = "https://level.travel/api/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Search parameters
SEARCH_PARAMS = {
    "from": "MOW",  # Moscow
    "to": "UTP",   # Pattaya
    "direct": "1",  # Direct flights only
    "adults": 2,
    "children": 0,
    "infants": 0,
    "meal": "all",  # All inclusive
    "hot_rating": "5",  # Minimum 5 stars
    "page": 1
}

# Database settings (relative to project root so it works inside container)
DATABASE_PATH = os.path.join(PROJECT_ROOT, "data", "tours.db")

# Logging
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "bot.log")
LOG_LEVEL = "INFO"