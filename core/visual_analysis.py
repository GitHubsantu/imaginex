import cv2
import numpy as np
from PIL import Image


def analyze_brightness(image_path):
    """
    Returns: 'Bright' | 'Dark'
    """
    img = Image.open(image_path).convert("L")  # grayscale
    arr = np.array(img)
    avg = arr.mean()

    return "Bright" if avg > 100 else "Dark"


def count_faces(image_path):
    """
    Returns: number of faces detected
    """
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    if w > 800:
        scale = 800 / w
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,     # less aggressive
        minNeighbors=8,      # reduce false positives
        minSize=(60, 60)     # ignore tiny fake faces
    )

    face_count = len(faces)

    # Safety cap
    if face_count > 10:
        face_count = 10

    return len(faces)
