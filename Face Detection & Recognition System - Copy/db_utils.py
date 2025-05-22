import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

DATABASE = 'users.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    if not os.path.exists(DATABASE):
        db = get_db()
        with open('database_schema.sql', 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        db.close()

def create_user(username, password, email, user_type='user'):
    db = get_db()
    try:
        # Check if user_type column exists in the users table
        cursor = db.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        has_user_type = False
        for col in columns:
            if col[1] == 'user_type':  # col[1] is the column name
                has_user_type = True
                break
        
        if has_user_type:
            # If user_type column exists, include it in the INSERT
            db.execute(
                'INSERT INTO users (username, password_hash, email, user_type) VALUES (?, ?, ?, ?)',
                (username, generate_password_hash(password), email, user_type)
            )
        else:
            # Otherwise, use the original schema without user_type
            db.execute(
                'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                (username, generate_password_hash(password), email)
            )
        
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        db.close()

def create_admin(username, password, email):
    # First check if user_type column exists, and create it if not
    db = get_db()
    try:
        cursor = db.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        has_user_type = False
        for col in columns:
            if col[1] == 'user_type':  # col[1] is the column name
                has_user_type = True
                break
        
        if not has_user_type:
            # Add the user_type column if it doesn't exist
            db.execute("ALTER TABLE users ADD COLUMN user_type TEXT DEFAULT 'user'")
            db.commit()
    except sqlite3.Error as e:
        print(f"Error checking for user_type column: {e}")
    finally:
        db.close()
    
    # Then create the admin user
    return create_user(username, password, email, user_type='admin')

def verify_user(username, password):
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    db.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def get_user_by_id(user_id):
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    db.close()
    return user 

def is_admin(user_id):
    """Check if a user has admin privileges.
    
    This function directly checks the database to see if the user has the admin role.
    """
    if not user_id:
        return False
        
    db = get_db()
    try:
        # Check if the users table has a user_type column
        cursor = db.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        has_user_type = False
        for col in columns:
            if col[1] == 'user_type':
                has_user_type = True
                break
        
        if not has_user_type:
            return False  # No user_type column means no admins
            
        # Check if this user is an admin
        admin_check = db.execute(
            'SELECT 1 FROM users WHERE id = ? AND user_type = "admin"', 
            (user_id,)
        ).fetchone()
        
        return admin_check is not None
    except:
        return False
    finally:
        db.close()

def save_recognition_record(person_name, image_path=None):
    """Save a face recognition event to the database."""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO recognition_records (person_name, detection_date, detection_time, image_path) VALUES (?, ?, ?, ?)',
            (person_name, date_str, time_str, image_path)
        )
        db.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        db.close()

def get_recognition_records(limit=100, working_hours_only=False):
    """Retrieve the most recent recognition records.
    
    Args:
        limit: Maximum number of records to return
        working_hours_only: If True, only returns records between 9AM and 5PM
    """
    db = get_db()
    
    if working_hours_only:
        records = db.execute(
            '''SELECT id, person_name, detection_date, detection_time, image_path, created_at 
               FROM recognition_records 
               WHERE CAST(substr(detection_time, 1, 2) AS INTEGER) BETWEEN 9 AND 17
               ORDER BY created_at DESC
               LIMIT ?''', 
            (limit,)
        ).fetchall()
    else:
        records = db.execute(
            '''SELECT id, person_name, detection_date, detection_time, image_path, created_at 
               FROM recognition_records 
               ORDER BY created_at DESC
               LIMIT ?''', 
            (limit,)
        ).fetchall()
    
    db.close()
    
    return records 