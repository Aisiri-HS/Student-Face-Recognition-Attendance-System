import cv2
import os
import streamlit as st
from utils import create_connection
from datetime import datetime
import numpy as np

# Load OpenCV LBPH recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
MODEL_PATH = "model/trained_model.yml"

def mark_attendance(student_id, name, cursor, conn):
    """Insert attendance record into DB with USN lookup."""
    cursor.execute("SELECT usn FROM students WHERE student_id=%s", (student_id,))
    result = cursor.fetchone()
    usn = result[0] if result else "UNKNOWN"

    now = datetime.now()
    date = now.date()
    time_ = now.strftime("%H:%M:%S")

    cursor.execute(
        "INSERT INTO attendance (student_id, name, usn, date, time) VALUES (%s, %s, %s, %s, %s)",
        (student_id, name, usn, date, time_)
    )
    conn.commit()

def recognize_faces():
    """Recognize faces in real-time and mark attendance."""
    # ✅ Check if trained model exists
    if not os.path.exists(MODEL_PATH):
        st.error("⚠️ No trained model found. Please train the model first.")
        return

    recognizer.read(MODEL_PATH)
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # ✅ Open DB connection once
    conn = create_connection()
    if conn is None:
        st.error("❌ Database connection failed!")
        return
    cursor = conn.cursor()

    # ✅ Start webcam
    cap = cv2.VideoCapture(0)
    frame_placeholder = st.empty()
    st.info("📷 Webcam started. Faces will be recognized in real-time. Press 'q' in terminal to stop.")

    recognized_ids = set()  # prevent multiple entries per session

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Convert to gray for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=8, minSize=(100, 100))

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]

            try:
                label, confidence = recognizer.predict(face_img)
            except:
                continue

            # ✅ Improved accuracy: lower confidence is better
            if label not in recognized_ids and confidence < 60:  
                cursor.execute("SELECT name FROM students WHERE student_id=%s", (label,))
                result = cursor.fetchone()
                if result:
                    name = result[0]
                    mark_attendance(label, name, cursor, conn)
                    recognized_ids.add(label)
                    st.success(f"✅ Attendance marked for {name} (ID: {label})")

            # Draw face rectangle + confidence
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"ID:{label} ({int(confidence)})", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Show in Streamlit
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb)

        # Stop if "q" is pressed in terminal
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # ✅ Cleanup
    cap.release()
    cursor.close()
    conn.close()
    st.success("✅ Attendance session ended.")
