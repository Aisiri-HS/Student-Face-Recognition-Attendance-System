import cv2
import os
import streamlit as st
from utils import create_connection
import time
import shutil

def reset_dataset_folder_if_empty():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]
    if count == 0:
        dataset_path = "dataset"
        if os.path.exists(dataset_path):
            shutil.rmtree(dataset_path)
        os.makedirs(dataset_path)
    cursor.close()
    conn.close()

def reset_student_id_if_empty():
    conn = create_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("ALTER TABLE students AUTO_INCREMENT = 1")
        conn.commit()
    cursor.close()
    conn.close()
def register_student(name, email, usn):
    # 0️⃣ Reset auto-increment if table is empty
    reset_student_id_if_empty()

    # 1️⃣ Connect to database
    conn = create_connection()
    if conn is None:
        st.error("Database connection failed! Check MySQL server and credentials.")
        return None

    cursor = conn.cursor()
    # 2️⃣ Insert student into DB
    cursor.execute(
        "INSERT INTO students (name, email, usn) VALUES (%s, %s, %s)",
        (name, email, usn)
    )
    student_id = cursor.lastrowid  # Get new student ID
    conn.commit()

    # 3️⃣ Create dataset folder using student_id
    dataset_path = "dataset"
    os.makedirs(dataset_path, exist_ok=True)          # Ensure 'dataset' folder exists
    folder_id = student_id                            # Folder named after student_id
    path = f"{dataset_path}/{folder_id}"
    os.makedirs(path, exist_ok=True)                  # Create folder for this student

    st.info("Webcam ready. Click 'Start Capture' to take images.")

    # ... rest of your webcam capture code


    # 2️⃣ Determine dataset folder
    dataset_path = "dataset"
    os.makedirs(dataset_path, exist_ok=True)

    # Use the database student_id as the folder name
    folder_id = student_id
    path = f"{dataset_path}/{folder_id}"
    os.makedirs(path, exist_ok=True)

    st.info("Webcam ready. Click 'Start Capture' to take images.")

    # 3️⃣ Initialize session_state for capture
    if "capture_started" not in st.session_state:
        st.session_state.capture_started = False

    # 4️⃣ Start capture when button is clicked
    if st.button("Start Capture") or st.session_state.capture_started:
        st.session_state.capture_started = True

        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        count = 0
        frame_placeholder = st.empty()

        while count < 2:  # Capture 20 images
            ret, frame = cap.read()
            if not ret:
                continue

            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                count += 1
                face_img = frame[y:y+h, x:x+w]  # SAVE COLOR IMAGE
                cv2.imwrite(f"{path}/{count}.jpg", face_img)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Show frame in Streamlit
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb)

            time.sleep(0.1)

        cap.release()
        st.session_state.capture_started = False
        st.success(f"Student {name} (USN: {usn}) registered successfully with {count} color images! Folder: {folder_id}")
        return student_id
