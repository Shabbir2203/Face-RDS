import cv2
import os

name = input("Enter name: ").strip().lower()
save_path = f"known_faces/{name}.jpg"
os.makedirs("known_faces", exist_ok=True)

cap = cv2.VideoCapture(0)
print("📸 Press 's' to save face | 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Register Face", frame)
    key = cv2.waitKey(1)

    if key == ord('s'):
        cv2.imwrite(save_path, frame)
        print(f"✅ Face saved as {save_path}")
        break
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("👋 Goodbye!")