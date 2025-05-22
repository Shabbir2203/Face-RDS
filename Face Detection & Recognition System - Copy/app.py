from flask import Flask, render_template, Response, request, redirect, url_for, flash, session
import cv2
import os
from detect import recognize_face, train_recognizer
import time
from db_utils import init_db, create_user, verify_user, get_user_by_id, save_recognition_record, get_recognition_records, create_admin, is_admin, get_db
from functools import wraps
import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize database
init_db()

# Global variables
camera = None
KNOWN_FACES_DIR = "known_faces"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        if not is_admin(session['user_id']):
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return camera

def generate_frames():
    camera = get_camera()
    last_detection_time = 0
    detection_interval = 3  # Seconds between database records to avoid duplicates
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Detect and recognize face
            name, face_crop = recognize_face(frame)

            # Draw rectangle and name if face is detected
            if face_crop is not None:
                height, width = frame.shape[:2]
                cv2.rectangle(frame, (width//4, height//4), 
                            (3*width//4, 3*height//4), (0, 255, 0), 2)
                cv2.putText(frame, name, (width//4, height//4 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Record detection to database at intervals
                current_time = time.time()
                if current_time - last_detection_time > detection_interval and name != "Unknown":
                    # Save the detection to database
                    save_recognition_record(name)
                    last_detection_time = current_time
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'user')
        
        user = verify_user(username, password)
        if user:
            # Set session values
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            # Handle admin login
            try:
                if user_type == 'admin':
                    # Check if this user has admin rights
                    db = get_db()
                    admin_check = db.execute(
                        'SELECT user_type FROM users WHERE id = ? AND user_type = "admin"', 
                        (user['id'],)
                    ).fetchone()
                    db.close()
                    
                    if not admin_check:
                        flash('You do not have admin privileges', 'error')
                        return redirect(url_for('login'))
                    
                    session['user_type'] = 'admin'
                else:
                    session['user_type'] = 'user'
            except:
                # Default to user if there's any error
                session['user_type'] = 'user'
            
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register_user'))
        
        if create_user(username, password, email):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists', 'error')
    
    return render_template('register_user.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/register_face', methods=['POST'])
@login_required
def register_face():
    name = request.form.get('name')
    image_data = request.form.get('image')
    
    if not name or not image_data:
        flash('Please provide both name and image', 'error')
        return redirect(url_for('index'))
    
    try:
        # Create directories if they don't exist
        if not os.path.exists(KNOWN_FACES_DIR):
            os.makedirs(KNOWN_FACES_DIR)
        
        # Convert base64 to image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        import base64
        import numpy as np
        
        # Decode base64 to image array
        img_data = base64.b64decode(image_data)
        img_array = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if frame is not None:
            # Get current date and time - use a more readable format with 12-hour time
            current_time = time.localtime()
            time_str = time.strftime("%Y%m%d_%I%M%p", current_time)  # Format: YYYYMMDD_HHMAM/PM
            
            # Save the image with date and time
            filename = f"{name}_{time_str}.jpg"
            filepath = os.path.join(KNOWN_FACES_DIR, filename)
            cv2.imwrite(filepath, frame)
            
            # Retrain the recognizer
            train_recognizer()
            flash(f'Successfully registered {name}!', 'success')
        else:
            flash('Failed to process image', 'error')
        
    except Exception as e:
        flash(f'Error registering face: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/recognize_face', methods=['GET', 'POST'])
@login_required
def recognize_face_route():
    if request.method == 'POST':
        # Handle face recognition
        camera = get_camera()
        success, frame = camera.read()
        if success:
            name, face_crop = recognize_face(frame)
            if face_crop is not None:
                # Format time with 12-hour clock
                current_time = time.localtime()
                time_str = time.strftime("%Y%m%d_%I%M%p", current_time)
                
                # Save the recognized face with date and time
                filename = f"recognized_{name}_{time_str}.jpg"
                filepath = os.path.join('static', 'recognized', filename)
                cv2.imwrite(filepath, face_crop)
                
                # Save record to database
                relative_path = os.path.join('recognized', filename)
                save_recognition_record(name, relative_path)
                
                flash(f'Face recognized as {name}!', 'success')
            else:
                flash('No face detected', 'error')
        else:
            flash('Failed to capture image', 'error')
        
        return redirect(url_for('index'))
    
    return render_template('recognize_face.html')

@app.route('/known_faces')
def known_faces():
    faces = []
    if os.path.exists(KNOWN_FACES_DIR):
        for filename in os.listdir(KNOWN_FACES_DIR):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                name = filename.split('_')[0]
                
                # Extract date/time info if available
                time_parts = filename.split('_')
                timestamp = time_parts[1] if len(time_parts) > 1 else ""
                
                faces.append({
                    'name': name,
                    'filename': filename,
                    'path': os.path.join(KNOWN_FACES_DIR, filename),
                    'timestamp': timestamp
                })
    return render_template('known_faces.html', faces=faces)

@app.route('/delete_face/<filename>')
def delete_face(filename):
    filepath = os.path.join(KNOWN_FACES_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        train_recognizer()
        flash('Face deleted successfully', 'success')
    return redirect(url_for('known_faces'))

@app.route('/recognition_history')
@admin_required
def recognition_history():
    working_hours_only = request.args.get('working_hours', 'false').lower() == 'true'
    records = get_recognition_records(working_hours_only=working_hours_only)
    return render_template('recognition_history.html', records=records, working_hours=working_hours_only)

@app.route('/register_admin', methods=['GET', 'POST'])
@admin_required
def register_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register_admin'))
        
        if create_admin(username, password, email):
            flash('Admin registration successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username or email already exists', 'error')
    
    return render_template('register_admin.html')

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin')
@admin_required
def admin_panel():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_management')
@admin_required
def admin_management():
    return render_template('admin_management.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = verify_user(username, password)
        if user:
            # Check if this user is an admin
            db = get_db()
            admin_check = db.execute(
                'SELECT 1 FROM users WHERE id = ? AND user_type = "admin"', 
                (user['id'],)
            ).fetchone()
            db.close()
            
            if not admin_check:
                flash('You are not authorized as an admin', 'error')
                return redirect(url_for('admin_login'))
            
            # Set session values
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = 'admin'
            
            flash('Admin login successful!', 'success')
            return redirect(url_for('simple_admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html')

@app.route('/simple_admin_dashboard')
@admin_required
def simple_admin_dashboard():
    working_hours_only = request.args.get('working_hours', 'false').lower() == 'true'
    records = get_recognition_records(working_hours_only=working_hours_only)
    return render_template('simple_admin_dashboard.html', records=records, working_hours=working_hours_only)

@app.route('/register_new_admin', methods=['GET', 'POST'])
@admin_required
def register_new_admin():
    success = False
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register_new_admin'))
        
        # Create a new admin user
        if create_admin(username, password, email):
            flash('Admin registration successful!', 'success')
            success = True
        else:
            flash('Username or email already exists', 'error')
    
    return render_template('register_new_admin.html', success=success)

if __name__ == '__main__':
    # Create required directories
    for directory in [KNOWN_FACES_DIR, 'static/recognized']:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    # Ensure the recognition_records table exists
    db = sqlite3.connect('users.db')
    db.execute('''
    CREATE TABLE IF NOT EXISTS recognition_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_name TEXT NOT NULL,
        detection_date DATE NOT NULL,
        detection_time TIME NOT NULL,
        image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    db.commit()
    db.close()
    
    app.run(debug=True)
