import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE = 'users.db'

def fix_admin():
    print("=== Admin Login Fix Tool ===")
    
    # Check if database exists
    if not os.path.exists(DATABASE):
        print(f"Error: Database '{DATABASE}' not found.")
        return
    
    # Connect to database
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check table structure
    print("\nChecking database structure...")
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    
    # Print column info for debugging
    print("\nCurrent users table structure:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check if user_type column exists
    has_user_type = False
    for col in columns:
        if col[1] == 'user_type':
            has_user_type = True
            break
    
    # Add user_type column if it doesn't exist
    if not has_user_type:
        print("\nAdding user_type column to users table...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN user_type TEXT DEFAULT 'user'")
            conn.commit()
            print("Column added successfully!")
        except sqlite3.Error as e:
            print(f"Error adding column: {e}")
            return
    
    # Ask user if they want to create an admin
    print("\nDo you want to create a new admin user? (y/n)")
    choice = input("> ").lower()
    
    if choice.startswith('y'):
        username = input("Enter admin username: ")
        email = input("Enter admin email: ")
        password = input("Enter admin password: ")
        
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"\nUser '{username}' already exists. Do you want to make this user an admin? (y/n)")
            update_choice = input("> ").lower()
            
            if update_choice.startswith('y'):
                cursor.execute("UPDATE users SET user_type = 'admin' WHERE username = ?", (username,))
                conn.commit()
                print(f"\nUser '{username}' has been made an admin!")
            else:
                print("Operation cancelled.")
        else:
            # Create new admin user
            try:
                cursor.execute(
                    'INSERT INTO users (username, password_hash, email, user_type) VALUES (?, ?, ?, ?)',
                    (username, generate_password_hash(password), email, 'admin')
                )
                conn.commit()
                print(f"\nSuccess! Admin user '{username}' has been created.")
            except sqlite3.Error as e:
                print(f"Error creating admin: {e}")
    
    # List all users in the database with their roles
    print("\nCurrent users in the database:")
    try:
        if has_user_type:
            cursor.execute("SELECT id, username, email, user_type FROM users")
        else:
            cursor.execute("SELECT id, username, email FROM users")
            
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the database.")
        else:
            for user in users:
                user_info = f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}"
                if has_user_type:
                    user_info += f", Role: {user['user_type'] or 'user'}"
                print(user_info)
    except sqlite3.Error as e:
        print(f"Error listing users: {e}")
    
    # Close the connection
    conn.close()
    print("\nAdmin fix process completed.")

if __name__ == "__main__":
    fix_admin() 