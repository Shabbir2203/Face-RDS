import cv2
import os
import numpy as np

# Initialize face detector and recognizer
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# Load known faces
KNOWN_FACES_DIR = "known_faces"
known_faces = []
known_names = []
label_map = {}

def train_recognizer():
    global known_names, label_map
    faces = []
    labels = []
    label_id = 0
    known_names = []
    label_map = {}
    
    # Create known_faces directory if it doesn't exist
    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)
        return
    
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(KNOWN_FACES_DIR, filename)
            # Extract only the name part before underscore or extension
            name = filename.split('_')[0]
            
            img = cv2.imread(path)
            if img is None:
                continue
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            detected_faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=4,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            if len(detected_faces) > 0:
                (x, y, w, h) = detected_faces[0]
                face = gray[y:y+h, x:x+w]
                face = cv2.resize(face, (100, 100))
                faces.append(face)
                
                if name not in label_map:
                    label_map[name] = label_id
                    label_id += 1
                    known_names.append(name)
                labels.append(label_map[name])
    
    if len(faces) > 0:
        face_recognizer.train(faces, np.array(labels))

# Initial training
train_recognizer()

def recognize_face(frame):
    if len(known_names) == 0:
        return "No trained faces", None
        
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces with optimized parameters
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    if len(faces) == 0:
        return "No Face", None
    
    for (x, y, w, h) in faces:
        face_roi = gray[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (100, 100))
        
        try:
            # Predict the face
            label_id, confidence = face_recognizer.predict(face_roi)
            
            # Lower confidence means better match in LBPH
            if confidence < 80:  # Reduced threshold for better recognition
                name = known_names[label_id]
            else:
                name = "Unknown"
        except Exception:
            name = "Unknown"
        
        # Return the name and face region
        return name, frame[y:y+h, x:x+w]
    
    return "Unknown", None

