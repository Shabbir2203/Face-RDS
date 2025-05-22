from db_utils import create_admin, init_db

# Initialize database
init_db()

# Demo admin credentials
USERNAME = "admin"
PASSWORD = "admin123"
EMAIL = "admin@example.com"

# Create the admin user
if create_admin(USERNAME, PASSWORD, EMAIL):
    print("==========================================================")
    print(f"Demo admin created successfully!")
    print("==========================================================")
    print(f"Username: {USERNAME}")
    print(f"Password: {PASSWORD}")
    print(f"Email: {EMAIL}")
    print("==========================================================")
    print("You can now login at the admin login page with these credentials")
else:
    print("Admin user could not be created (it might already exist)")
    print("Try a different username or check the database") 