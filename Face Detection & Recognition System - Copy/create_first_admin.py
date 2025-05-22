from db_utils import create_admin, init_db

def create_first_admin():
    print("=== Create First Admin User ===")
    print("This script will create an admin user with full access to the system.")
    
    # Initialize database if it doesn't exist
    init_db()
    
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    
    if create_admin(username, password, email):
        print(f"\nSuccess! Admin user '{username}' has been created.")
        print("You can now login to the system with admin privileges.")
    else:
        print("\nError: Failed to create admin user. Username or email may already exist.")

if __name__ == "__main__":
    create_first_admin() 