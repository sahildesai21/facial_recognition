import cv2
import os
from datetime import datetime
import time

PERSON_NAME = "siddu"  # Change this to the name of the person

def create_folder(name):
    dataset_folder = "dataset"
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)
    
    person_folder = os.path.join(dataset_folder, name)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)
    return person_folder

def capture_photos(name):
    folder = create_folder(name)
    camera = cv2.VideoCapture(0)  # Change to 1 if the USB webcam is not the default

    if not camera.isOpened():
        print("Error: Could not access the camera.")
        return
    
    # Set the camera resolution
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Width of the window
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Height of the window
    
    time.sleep(2)  # Warm-up time for camera
    photo_count = 0
    print(f"Taking photos for {name}. Press SPACE to capture, 'q' to quit.")
    
    # Create a window with specific size
    cv2.namedWindow('Capture', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Capture', 640, 480)  # Resize the window to match the camera resolution
    
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Failed to capture image")
            break
        
        cv2.imshow('Capture', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Space key to capture photo
            photo_count += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.jpg"
            filepath = os.path.join(folder, filename)
            cv2.imwrite(filepath, frame)
            print(f"Photo {photo_count} saved: {filepath}")
        elif key == ord('q'):  # Q key to quit
            break
    
    camera.release()
    cv2.destroyAllWindows()
    print(f"Capture complete. {photo_count} photos saved for {name}.")

if __name__ == "__main__":
    capture_photos(PERSON_NAME)

