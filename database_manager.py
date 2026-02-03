import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "agentic_system.db"

def init_db():
    """Creates the database tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Table for raw sensor readings
    c.execute('''CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    temperature REAL,
                    voltage REAL,
                    current REAL
                )''')

    # Table for Agent decisions/events
    c.execute('''CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    event_type TEXT,
                    message TEXT
                )''')
    
    conn.commit()
    conn.close()

def clear_db():
    """Wipes all data AND resets the auto-increment ID counter."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Delete actual data
    c.execute("DELETE FROM readings")
    c.execute("DELETE FROM events")
    
    # 2. Reset the ID counters in SQLite's internal sequence table
    c.execute("DELETE FROM sqlite_sequence WHERE name='readings'")
    c.execute("DELETE FROM sqlite_sequence WHERE name='events'")
    
    conn.commit()
    conn.close()

def log_data(temp, voltage, current):
    """Saves sensor data to DB."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%H:%M:%S")
    c.execute("INSERT INTO readings (timestamp, temperature, voltage, current) VALUES (?, ?, ?, ?)",
              (timestamp, temp, voltage, current))
    conn.commit()
    conn.close()

def log_event(event_type, message):
    """Saves an agent decision or alert."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%H:%M:%S")
    c.execute("INSERT INTO events (timestamp, event_type, message) VALUES (?, ?, ?)",
              (timestamp, event_type, message))
    conn.commit()
    conn.close()

def get_recent_readings(limit=100):
    """Fetch recent data for the Dashboard graphs."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT * FROM readings ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df.iloc[::-1] # Reverse so oldest is first for plotting

def get_recent_events(limit=10):
    """Fetch recent logs for the Dashboard console."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT * FROM events ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df