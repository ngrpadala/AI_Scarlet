import os
import cv2
import face_recognition
import json
from scarlet.config import FACE_DIR, MEMORY_PATH

# Load known faces
_known_encs = []
_known_names = []
for fn in os.listdir(FACE_DIR):
    if fn.lower().endswith((".jpg", ".png")):
        img = face_recognition.load_image_file(os.path.join(FACE_DIR, fn))
        encs = face_recognition.face_encodings(img)
        if encs:
            _known_encs.append(encs[0])
            _known_names.append(os.path.splitext(fn)[0].lower())

def load_memory():
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_PATH, "w") as f:
        json.dump(data, f, indent=2)

def detect_face(timeout=3):
    """
    Captures a snapshot from USB webcam using OpenCV.
    Returns detected name, or 'unknown'.
    Special handling if Lalitha is detected.
    """
    try:
        cap = cv2.VideoCapture(0)  # /dev/video0
        if not cap.isOpened():
            print("[Error] Unable to open webcam")
            return "unknown"

        # Set timeout capture in seconds
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.read()  # Warm up
        ret, frame = cap.read()
        cap.release()

        if not ret:
            print("[Error] Failed to capture image from webcam")
            return "unknown"

        # Save temp image (optional)
        cv2.imwrite("/dev/shm/live.jpg", frame)

        # Proceed with face recognition
        img = face_recognition.load_image_file("/dev/shm/live.jpg")
        encs = face_recognition.face_encodings(img)
        if not encs:
            return "unknown"

        face = encs[0]
        matches = face_recognition.compare_faces(_known_encs, face, tolerance=0.48)
        if True in matches:
            name = _known_names[matches.index(True)]

            if name == "lalitha":
                memory = load_memory()
                if "akka_permission" not in memory:
                    memory["akka_permission"] = "pending"
                    save_memory(memory)
                return "lalitha"

            return name

    except Exception as e:
        print("[Face Recognition Error]:", e)

    return "unknown"

