import sqlite3
from db_utils import DATABASE

def migrate_add_user_type():
    print("Running user_type column migration...")
    
    # Connect to the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    has_user_type = False
    for col in columns:
        if col[1] == 'user_type':  # col[1] is the column name
            has_user_type = True
            break
    
    if not has_user_type:
        print("Adding user_type column to users table...")
        try:
            # SQLite doesn't support ALTER TABLE ADD COLUMN with constraints directly
            # So we'll add it without the NOT NULL constraint first
            cursor.execute("ALTER TABLE users ADD COLUMN user_type TEXT DEFAULT 'user'")
            
            # Then update existing rows
            cursor.execute("UPDATE users SET user_type = 'user' WHERE user_type IS NULL")
            
            print("Column added successfully!")
        except sqlite3.Error as e:
            print(f"Error: {e}")
    else:
        print("user_type column already exists.")
    
    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate_add_user_type() 