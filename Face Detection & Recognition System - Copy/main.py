import cv2
from detect import recognize_face

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    while True:
        # Read frame from webcam
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break

        # Detect and recognize face
        name, face_crop = recognize_face(frame)
        
        # Draw rectangle and name if face is detected
        if face_crop is not None:
            height, width = frame.shape[:2]
            # Draw rectangle around the face
            cv2.rectangle(frame, (width//4, height//4), 
                        (3*width//4, 3*height//4), (0, 255, 0), 2)
            
            # Put name text above the rectangle
            cv2.putText(frame, name, (width//4, height//4 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow('Face Recognition', frame)

        # Break loop on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 