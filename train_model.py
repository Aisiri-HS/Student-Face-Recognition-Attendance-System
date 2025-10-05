
import cv2
import os
import numpy as np
from PIL import Image
from pathlib import Path

def train_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    dataset_path = Path("dataset")
    faces = []
    ids = []

    for student_folder in dataset_path.iterdir():
        student_id = int(student_folder.name)
        for image_path in student_folder.iterdir():
            img = Image.open(image_path).convert("L")
            faces.append(np.array(img, 'uint8'))
            ids.append(student_id)

    recognizer.train(faces, np.array(ids))
    os.makedirs("model", exist_ok=True)
    recognizer.write("model/trained_model.yml")
    print("Model trained successfully.")

if __name__ == "__main__":
    train_model()
