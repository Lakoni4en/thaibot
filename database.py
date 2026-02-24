import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional
from dataclasses import asdict
from config.settings import DATABASE_PATH
import sys
sys.path.append('.')
from parser import Tour

logger = logging.getLogger(__name__)

def init_db():
    """
    Initialize database tables
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tours (
                    id INTEGER PRIMARY KEY,
                    tour_id TEXT UNIQUE,
                    title TEXT,
                    price INTEGER,
                    departure_date TEXT,
                    nights INTEGER,
                    hotel_name TEXT,
                    hotel_rating INTEGER,
                    meal_type TEXT,
                    flight_info TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    subscribed BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_price ON tours(price)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_departure ON tours(departure_date)')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=20.0)
        conn.row_factory = sqlite3.Row
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def save_tours(tours: List[Tour]):
    """
    Save tours to database
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for tour in tours:
                tour_dict = asdict(tour)
                cursor.execute('''
                    INSERT OR REPLACE INTO tours 
                    (tour_id, title, price, departure_date, nights, hotel_name, hotel_rating, meal_type, flight_info, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tour_dict['tour_id'],
                    tour_dict['title'],
                    tour_dict['price'],
                    tour_dict['departure_date'],
                    tour_dict['nights'],
                    tour_dict['hotel_name'],
                    tour_dict['hotel_rating'],
                    tour_dict['meal_type'],
                    tour_dict['flight_info'],
                    tour_dict['url']
                ))
            conn.commit()
            logger.info(f"Saved {len(tours)} tours to database")
            
    except Exception as e:
        logger.error(f"Error saving tours to database: {e}")
        raise

def get_existing_tour_ids() -> List[str]:
    """
    Get all existing tour IDs from database
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT tour_id FROM tours')
            return [row['tour_id'] for row in cursor.fetchall()]
            
    except Exception as e:
        logger.error(f"Error getting existing tour IDs: {e}")
        return []

def get_latest_tours(limit: int = 10) -> List[sqlite3.Row]:
    """
    Get latest tours sorted by price
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM tours 
                ORDER BY price ASC, created_at DESC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
            
    except Exception as e:
        logger.error(f"Error getting latest tours: {e}")
        return []

def save_user(user_data: dict):
    """
    Save or update user data
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (
                user_data['id'],
                user_data.get('username'),
                user_data.get('first_name'),
                user_data.get('last_name')
            ))
            conn.commit()
            logger.info(f"User {user_data['id']} saved to database")
            
    except Exception as e:
        logger.error(f"Error saving user: {e}")
        raise