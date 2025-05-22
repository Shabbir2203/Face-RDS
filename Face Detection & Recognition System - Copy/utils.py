import os
import face_recognition

def load_known_faces(known_face_dir='known_faces'):
    known_encodings = []
    known_names = []

    for file in os.listdir(known_face_dir):
        if file.endswith(('.jpg', '.png')):
            path = os.path.join(known_face_dir, file)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                name = os.path.splitext(file)[0].replace("_", " ").title()
                known_names.append(name)
    return known_encodings, known_names
