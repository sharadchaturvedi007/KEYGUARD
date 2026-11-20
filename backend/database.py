import sqlite3
import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "database", "keyguard.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_category TEXT,
            session_id TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            risk_score INTEGER,
            risk_level TEXT,
            indicators TEXT
        )
    """)

    # Add indicators column to an older database if needed
    cursor.execute("PRAGMA table_info(assessments)")
    columns = [row[1] for row in cursor.fetchall()]

    if "indicators" not in columns:
        cursor.execute("""
            ALTER TABLE assessments
            ADD COLUMN indicators TEXT
        """)

    conn.commit()
    conn.close()


def save_event(category, session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO activity_logs
        (timestamp, event_category, session_id)
        VALUES (?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        category,
        session_id
    ))

    conn.commit()
    conn.close()


def get_history():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM activity_logs
        ORDER BY id DESC
        LIMIT 100
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def save_assessment(result):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO assessments
        (timestamp, risk_score, risk_level, indicators)
        VALUES (?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        result["risk_score"],
        result["risk_level"],
        json.dumps(result["indicators"])
    ))

    conn.commit()
    conn.close()


def get_assessment_history():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM assessments
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    history = []

    for row in rows:

        history.append({
            "id": row[0],
            "timestamp": row[1],
            "risk_score": row[2],
            "risk_level": row[3],
            "indicators": json.loads(row[4]) if row[4] else []
        })

    return history