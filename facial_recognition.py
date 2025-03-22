import cv2
import mediapipe as mp
import numpy as np
import time
import pickle
import face_recognition
from twilio.rest import Client
import requests
import threading
from scipy.spatial import distance as dist

# Twilio Credentials
account_sid = 'AC0f0e455be9fa6e83a44d16889e8eb6e4'  
auth_token = 'b1609506b11ee56df0e07b6070492d9c'  
client = Client(account_sid, auth_token)
recipient_phone = '+919108211783'  


PI_B_URL = "http://192.168.20.147:5000/unlock"  

# Function to send SMS in a separate thread
def send_sms_async(message, to):
    def send():
        try:
            msg = client.messages.create(
                body=message,
                from_='+16163105003',  # Your Twilio number
                to=to
            )
            print(f"Message sent with SID: {msg.sid}")
        except Exception as e:
            print("Failed to send SMS:", e)

    threading.Thread(target=send).start()

# Function to send Unlock Request in a separate thread
def send_unlock_request():
    def unlock():
        try:
            response = requests.post(PI_B_URL, json={"auth": "granted"})
            try:
                data = response.json()  # Attempt to parse JSON response
                print("Unlock request sent to Pi B:", data)
            except ValueError:
                print("Failed to parse JSON response. Raw response:", response.text)
        except Exception as e:
            print("Failed to send unlock request:", e)

    threading.Thread(target=unlock).start()

# Load known face encodings
print("[INFO] Loading encodings...")
with open("encodings.pickle", "rb") as f:
    data = pickle.loads(f.read())

known_face_encodings = data.get("encodings", [])
known_face_names = data.get("names", [])

# Initialize camera and Mediapipe
camera = cv2.VideoCapture(0)
mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, min_detection_confidence=0.5)

# Eye Aspect Ratio (EAR) calculation
def calculate_ear(eye):
    A = dist.euclidean(eye[1], eye[5])  # Vertical distance
    B = dist.euclidean(eye[2], eye[4])  # Vertical distance
    C = dist.euclidean(eye[0], eye[3])  # Horizontal distance
    ear = (A + B) / (2.0 * C)
    return ear

# Constants for blink detection
EAR_THRESHOLD = 0.2  # Below this value, eyes are considered closed
BLINK_FRAMES_REQUIRED = 1  # Number of frames eyes must be closed to count as a blink

# Track blinks
blink_counter = 0
blinks_detected = False

# Frame counter for optimization
frame_counter = 0
last_sms_time = time.time()  # To track the last SMS sent
sms_delay = 2  # 5 seconds delay between SMS

while True:
    ret, frame = camera.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame_counter += 1
    if frame_counter % 5 != 0:  # Process every 5th frame
        continue

    small_frame = cv2.resize(frame, (320, 240))  # Resize for faster processing
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    results = face_detection.process(rgb_frame)
    mesh_results = face_mesh.process(rgb_frame)

    face_names = []
    detected_face = False

    if results.detections:
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            x, y, w, h = (int(bbox.xmin * small_frame.shape[1]),
                          int(bbox.ymin * small_frame.shape[0]),
                          int(bbox.width * small_frame.shape[1]),
                          int(bbox.height * small_frame.shape[0]))

            detected_face = True

            if y >= 0 and y + h <= small_frame.shape[0] and x >= 0 and x + w <= small_frame.shape[1]:
                face_encodings = face_recognition.face_encodings(small_frame, known_face_locations=[(y, x + w, y + h, x)])

                name = "Unknown"
                if face_encodings:
                    face_encoding = face_encodings[0]
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.35)
                    if True in matches:
                        match_index = matches.index(True)
                        name = known_face_names[match_index]

                        # *Blink Detection*
                        if mesh_results.multi_face_landmarks:
                            for face_landmarks in mesh_results.multi_face_landmarks:
                                left_eye = [
                                    (face_landmarks.landmark[i].x * small_frame.shape[1],
                                     face_landmarks.landmark[i].y * small_frame.shape[0])
                                    for i in [362, 385, 387, 263, 373, 380]
                                ]
                                right_eye = [
                                    (face_landmarks.landmark[i].x * small_frame.shape[1],
                                     face_landmarks.landmark[i].y * small_frame.shape[0])
                                    for i in [33, 160, 158, 133, 153, 144]
                                ]

                                ear_left = calculate_ear(left_eye)
                                ear_right = calculate_ear(right_eye)
                                avg_ear = (ear_left + ear_right) / 2.0

                                if avg_ear < EAR_THRESHOLD:
                                    blink_counter += 1
                                else:
                                    if blink_counter >= BLINK_FRAMES_REQUIRED:
                                        blinks_detected = True  # Mark user as real
                                    blink_counter = 0  # Reset

                        if blinks_detected:
                            if name != "Unknown" and time.time() - last_sms_time >= sms_delay:
                                send_sms_async(f"Hello {name}, you have been authenticated!", recipient_phone)
                                send_unlock_request()
                                last_sms_time = time.time()
                        else:
                            print(f"⚠ Liveness Check Failed: {name} did not blink!")

                face_names.append(name)

    # If no face detected, reset previous positions
    if not detected_face:
        blink_counter = 0
        blinks_detected = False

    cv2.imshow('Video', small_frame)

    if cv2.waitKey(1) == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()