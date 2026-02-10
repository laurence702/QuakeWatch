import sqlite3
import datetime
from geopy.geocoders import Nominatim
from pathlib import Path

# Define the database path relative to this file
DB_PATH = Path(__file__).parent.parent / "subscriptions.db"
TABLE_NAME = "subscriptions"

def init_db():
    """Initializes the database and creates the subscriptions table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            location_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_subscriber(email: str, location: str):
    """
    Adds a new subscriber to the database.
    Geocodes the location string to get latitude and longitude.
    """
    geolocator = Nominatim(user_agent="earthquake_alerter")
    try:
        location_data = geolocator.geocode(location)
        if not location_data:
            raise ValueError(f"Could not geocode location: {location}")

        lat = location_data.latitude
        lon = location_data.longitude
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            INSERT INTO {TABLE_NAME} (email, location_name, latitude, longitude, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
            location_name=excluded.location_name,
            latitude=excluded.latitude,
            longitude=excluded.longitude
        """, (email, location, lat, lon, datetime.datetime.now(datetime.UTC))) # Fixed deprecation warning
        
        conn.commit()
    except Exception as e:
        print(f"Error adding subscriber: {e}")
        # In a real app, you'd want more robust error handling
        raise
    finally:
        if conn:
            conn.close()

def get_all_subscribers():
    """Fetches all subscribers from the database."""
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dictionaries for easier use
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT email, latitude, longitude FROM {TABLE_NAME}")
        subscribers = [dict(row) for row in cursor.fetchall()]
        return subscribers
    except Exception as e:
        print(f"Error fetching subscribers: {e}")
        return []
    finally:
        if conn:
            conn.close()
