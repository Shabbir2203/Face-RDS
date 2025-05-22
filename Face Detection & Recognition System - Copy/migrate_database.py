import sqlite3
from db_utils import DATABASE

def migrate_database():
    print("Running database migration...")
    
    # Connect to the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recognition_records'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("Creating recognition_records table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recognition_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_name TEXT NOT NULL,
            detection_date DATE NOT NULL,
            detection_time TIME NOT NULL,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Table created successfully!")
    else:
        print("recognition_records table already exists.")
    
    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate_database() 