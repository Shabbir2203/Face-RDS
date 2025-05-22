# Face Detection & Recognition System

This is a real-time face detection and recognition system using OpenCV.

## Setup

1. Install the required dependencies:
```bash
pip install opencv-python
pip install numpy
```

2. Create a folder named `known_faces` in the project directory
3. Add photos of known faces to the `known_faces` folder:
   - Name the files with the person's name (e.g., "john.jpg", "sarah.png")
   - Each photo should clearly show one face
   - Supported formats: JPG, JPEG, PNG

## Usage

1. Run the program:
```bash
python main.py
```

2. The webcam will open and start detecting faces
3. If a face is recognized, it will display the name from the training photos
4. Unknown faces will be labeled as "Unknown"
5. Press 'q' to quit the program

## Features

- Real-time face detection
- Face recognition for known faces
- Automatic retraining when new faces are added
- Simple and intuitive interface 