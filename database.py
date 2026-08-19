import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# =====================================================
# DATABASE PATH
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "meetsphere.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


PASSWORD_ITERATIONS = 600_000


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password, stored_password):
    if stored_password.startswith("pbkdf2_sha256$"):
        _, iterations, salt_hex, digest_hex = stored_password.split("$", 3)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(digest.hex(), digest_hex)

    legacy_digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy_digest, stored_password)


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
        meeting_link TEXT,
        owner_username TEXT,
        archived_at TEXT
    )
    """)

    conn.commit()

    cursor.execute("PRAGMA table_info(meetings)")
    columns = [row[1] for row in cursor.fetchall()]
    if "meeting_link" not in columns:
        cursor.execute("ALTER TABLE meetings ADD COLUMN meeting_link TEXT")
        conn.commit()

    if "owner_username" not in columns:
        cursor.execute("ALTER TABLE meetings ADD COLUMN owner_username TEXT")
        conn.commit()

    if "archived_at" not in columns:
        cursor.execute("ALTER TABLE meetings ADD COLUMN archived_at TEXT")
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


def create_meeting_messages_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meeting_messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meeting_id INTEGER NOT NULL,
        sender_username TEXT NOT NULL,
        sender_name TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(meeting_id) REFERENCES meetings(id)
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
    create_meeting_messages_table()
    archive_expired_meetings()


def meeting_datetime(date_value, time_value):
    for date_format in ("%Y-%m-%d %H:%M", "%m/%d/%Y %I:%M %p", "%m/%d/%Y %H:%M"):
        try:
            return datetime.strptime(f"{date_value} {time_value}", date_format)
        except ValueError:
            continue
    return None


def archive_expired_meetings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, meeting_date, meeting_time FROM meetings WHERE archived_at IS NULL")
    expired_ids = [
        row[0]
        for row in cursor.fetchall()
        if meeting_datetime(row[1], row[2]) and meeting_datetime(row[1], row[2]) <= datetime.now()
    ]
    if expired_ids:
        cursor.executemany(
            "UPDATE meetings SET archived_at=? WHERE id=?",
            [(datetime.now(timezone.utc).isoformat(), meeting_id) for meeting_id in expired_ids]
        )
        conn.commit()
    conn.close()


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

    cursor.execute("""
        SELECT *
        FROM users
        WHERE username=?
    """, (
        username.strip(),
    ))

    user = cursor.fetchone()

    if user and verify_password(password, user[4]):
        if not user[4].startswith("pbkdf2_sha256$"):
            cursor.execute(
                "UPDATE users SET password=? WHERE username=?",
                (hash_password(password), username.strip())
            )
            conn.commit()
    else:
        user = None

    conn.close()

    return user


# =====================================================
# ADD MEETING
# =====================================================

def add_meeting(title, date, time, duration, description, owner_username=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO meetings
        (title, meeting_date, meeting_time, duration, description, owner_username)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        title,
        date,
        time,
        duration,
        description,
        owner_username
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

def get_all_meetings(owner_username=None):
    conn = get_connection()
    cursor = conn.cursor()

    if owner_username is None:
        cursor.execute("SELECT * FROM meetings WHERE archived_at IS NULL ORDER BY id DESC")
    else:
        cursor.execute(
            "SELECT * FROM meetings WHERE archived_at IS NULL AND (owner_username = ? OR owner_username IS NULL) ORDER BY id DESC",
            (owner_username,)
        )

    meetings = cursor.fetchall()

    conn.close()

    return meetings


def get_meeting_history(owner_username=None):
    conn = get_connection()
    cursor = conn.cursor()
    if owner_username is None:
        cursor.execute("SELECT * FROM meetings WHERE archived_at IS NOT NULL ORDER BY archived_at DESC")
    else:
        cursor.execute(
            "SELECT * FROM meetings WHERE archived_at IS NOT NULL AND (owner_username = ? OR owner_username IS NULL) ORDER BY archived_at DESC",
            (owner_username,)
        )
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

def delete_meeting(meeting_id, owner_username=None):
    conn = get_connection()
    cursor = conn.cursor()

    if owner_username is None:
        cursor.execute("DELETE FROM meetings WHERE id=?", (meeting_id,))
    else:
        cursor.execute(
            "DELETE FROM meetings WHERE id=? AND owner_username=?",
            (meeting_id, owner_username)
        )

    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted > 0


def get_meeting_messages(meeting_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, sender_username, sender_name, message, created_at FROM meeting_messages WHERE meeting_id=? ORDER BY id ASC",
        (meeting_id,)
    )
    messages = cursor.fetchall()
    conn.close()
    return messages


def add_meeting_message(meeting_id, sender_username, sender_name, message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO meeting_messages(meeting_id, sender_username, sender_name, message, created_at) VALUES (?, ?, ?, ?, ?)",
        (meeting_id, sender_username, sender_name, message, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    message_id = cursor.lastrowid
    conn.close()
    return message_id


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