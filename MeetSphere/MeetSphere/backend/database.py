import hashlib
import sqlite3
import os

# =====================================================
# DATABASE PATH
# =====================================================

os.makedirs("data", exist_ok=True)

DB_PATH = "data/meetsphere.db"


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def build_meeting_link(meeting_id):
    return f"https://meetsphere.app/meeting/{meeting_id}"


# =====================================================
# CONNECT DATABASE
# =====================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# =====================================================
# CREATE USERS TABLE
# =====================================================

def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# =====================================================
# CREATE MEETINGS TABLE
# =====================================================

def create_meeting_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meetings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        meeting_date TEXT NOT NULL,
        meeting_time TEXT NOT NULL,
        duration TEXT NOT NULL,
        description TEXT,
        meeting_link TEXT
    )
    """)

    conn.commit()

    cursor.execute("PRAGMA table_info(meetings)")
    columns = [row[1] for row in cursor.fetchall()]
    if "meeting_link" not in columns:
        cursor.execute("ALTER TABLE meetings ADD COLUMN meeting_link TEXT")
        conn.commit()
        cursor.execute("SELECT id FROM meetings WHERE meeting_link IS NULL OR meeting_link = ''")
        rows = cursor.fetchall()
        for row in rows:
            meeting_id = row[0]
            cursor.execute(
                "UPDATE meetings SET meeting_link = ? WHERE id = ?",
                (build_meeting_link(meeting_id), meeting_id)
            )
        conn.commit()

    conn.close()


def create_user_settings_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings(
        username TEXT PRIMARY KEY,
        mic_enabled INTEGER DEFAULT 1,
        camera_enabled INTEGER DEFAULT 1,
        notifications_enabled INTEGER DEFAULT 1,
        dark_mode INTEGER DEFAULT 0,
        display_name TEXT,
        email TEXT,
        FOREIGN KEY(username) REFERENCES users(username)
    )
    """)

    conn.commit()
    conn.close()


# =====================================================
# CREATE DATABASE
# =====================================================

def create_database():
    create_users_table()
    create_meeting_table()
    create_user_settings_table()


# =====================================================
# REGISTER USER
# =====================================================

def register_user(name, email, username, password):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    try:
        cursor.execute("""
            INSERT INTO users(name, email, username, password)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            username,
            hashed_password
        ))

        cursor.execute("""
            INSERT OR REPLACE INTO user_settings(
                username,
                display_name,
                email
            )
            VALUES (?, ?, ?)
        """, (
            username,
            name,
            email
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        raise

    finally:
        conn.close()


# =====================================================
# LOGIN
# =====================================================

def check_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username=? AND password=?
    """, (
        username.strip(),
        hashed_password
    ))

    user = cursor.fetchone()

    conn.close()

    return user


# =====================================================
# ADD MEETING
# =====================================================

def add_meeting(title, date, time, duration, description):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO meetings
        (title, meeting_date, meeting_time, duration, description)
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        date,
        time,
        duration,
        description
    ))

    meeting_id = cursor.lastrowid
    meeting_link = build_meeting_link(meeting_id)
    cursor.execute(
        "UPDATE meetings SET meeting_link = ? WHERE id = ?",
        (meeting_link, meeting_id)
    )

    conn.commit()
    conn.close()
    return meeting_link


def add_meeting_with_id(meeting_id, title, date, time, duration, description):
    """Insert a meeting with an explicit ID. Raises IntegrityError on duplicate id."""
    conn = get_connection()
    cursor = conn.cursor()

    meeting_link = build_meeting_link(meeting_id)
    cursor.execute("""
        INSERT INTO meetings
        (id, title, meeting_date, meeting_time, duration, description, meeting_link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        meeting_id,
        title,
        date,
        time,
        duration,
        description,
        meeting_link
    ))

    conn.commit()
    conn.close()
    return meeting_link


# =====================================================
# GET ALL MEETINGS
# =====================================================

def get_all_meetings():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM meetings
        ORDER BY id DESC
    """)

    meetings = cursor.fetchall()

    conn.close()

    return meetings


# =====================================================
# GET MEETING BY ID
# =====================================================

def get_meeting_by_id(meeting_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM meetings WHERE id = ?",
        (meeting_id,)
    )

    meeting = cursor.fetchone()
    conn.close()

    return meeting


# =====================================================
# DELETE MEETING
# =====================================================

def delete_meeting(meeting_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM meetings WHERE id=?",
        (meeting_id,)
    )

    conn.commit()
    conn.close()


# =====================================================
# GET USER DETAILS
# =====================================================

def get_user(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    return user


def update_user(username, name, email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET name=?, email=? WHERE username=?",
        (name, email, username)
    )

    cursor.execute(
        "INSERT OR REPLACE INTO user_settings(username, display_name, email) VALUES (?, ?, ?)",
        (username, name, email)
    )

    conn.commit()
    conn.close()


def update_user_password(username, new_password):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(new_password)

    cursor.execute(
        "UPDATE users SET password=? WHERE username=?",
        (hashed_password, username)
    )

    conn.commit()
    conn.close()


def get_user_settings(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM user_settings WHERE username=?",
        (username,)
    )

    settings = cursor.fetchone()
    conn.close()

    return settings


def save_user_settings(username, mic_enabled, camera_enabled, notifications_enabled, dark_mode, display_name, email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR REPLACE INTO user_settings(username, mic_enabled, camera_enabled, notifications_enabled, dark_mode, display_name, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            username,
            1 if mic_enabled else 0,
            1 if camera_enabled else 0,
            1 if notifications_enabled else 0,
            1 if dark_mode else 0,
            display_name,
            email
        )
    )

    cursor.execute(
        "UPDATE users SET name=?, email=? WHERE username=?",
        (display_name, email, username)
    )

    conn.commit()
    conn.close()


# =====================================================
# INITIALIZE DATABASE
# =====================================================

create_database()