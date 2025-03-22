import os
from imutils import paths
import face_recognition
import pickle
import cv2

print("[INFO] Start processing faces...")
imagePaths = list(paths.list_images("dataset"))
knownEncodings = []
knownNames = []

for (i, imagePath) in enumerate(imagePaths):
    print(f"[INFO] Processing image {i + 1}/{len(imagePaths)}")
    name = imagePath.split(os.path.sep)[-2]
    image = cv2.imread(imagePath)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Resize for faster processing
    small_rgb = cv2.resize(rgb, (0, 0), fx=0.5, fy=0.5)
    
    # Use 'cnn' model for high accuracy
    boxes = face_recognition.face_locations(small_rgb, model="cnn")
    encodings = face_recognition.face_encodings(small_rgb, boxes)
    
    for encoding in encodings:
        knownEncodings.append(encoding)
        knownNames.append(name)

print("[INFO] Serializing encodings...")
data = {"encodings": knownEncodings, "names": knownNames}
with open("encodings.pickle", "wb") as f:
    f.write(pickle.dumps(data))

print("[INFO] Training complete. Encodings saved to 'encodings.pickle'.")

