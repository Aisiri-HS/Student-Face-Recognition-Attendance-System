import streamlit as st
import pandas as pd
from utils import create_connection
from student_registration import register_student
from train_model import train_model
from face_recognition import recognize_faces
from attendance_utils import get_attendance_percentage

# ---------------- Page Config ----------------
st.set_page_config(page_title="Face Recognition Attendance", layout="wide", page_icon="📸")

# ---------------- Background & Custom CSS ----------------
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.7); color: white; }
    .stTitle { font-size: 2.5rem; font-weight: bold; color: #FFD700; text-align: center; }
    .card { background-color: rgba(0, 0, 0, 0.6); padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.3); transition: transform 0.3s; }
    .card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.5); }
    .stButton>button { background: #FFD700; color: #000; font-weight: bold; border-radius: 10px; padding: 0.6em 1.2em; margin-top: 10px; width: 100%; font-size: 1rem; transition: background 0.3s; }
    .stButton>button:hover { background: #ffea00; }
    input, textarea { border-radius: 10px; padding: 8px; border: 2px solid #FFD700; background-color: rgba(255,255,255,0.1); color: white; }
    .stDataFrame table { background-color: rgba(0,0,0,0.5); color: white; }
    </style>
""", unsafe_allow_html=True)

# ---------------- Title ----------------
st.markdown('<h1 class="stTitle">📸 Student Face Recognition Attendance System</h1>', unsafe_allow_html=True)
st.write("---")

# ---------------- Sidebar Menu ----------------
menu = ["Home", "Register Student", "Train Model", "Start Attendance", "Attendance Report", "Individual Attendance"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- Home ----------------
if choice == "Home":
    st.markdown('<div class="card"><h2>Welcome!</h2><p>Use the sidebar to navigate through features.</p></div>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1508780709619-79562169bc64?auto=format&fit=crop&w=1200&q=80", use_column_width=True)
    st.markdown("""<div style='text-align: center; margin-top: 20px; color: #FFD700; font-weight: bold;'>© 2024 Aisiri H S</div>""", unsafe_allow_html=True)

# ---------------- Register Student ----------------
elif choice == "Register Student":
    st.markdown('<div class="card"><h2>Register a New Student</h2></div>', unsafe_allow_html=True)
    name = st.text_input("Student Name")
    usn = st.text_input("USN")
    email = st.text_input("Email")

    if st.button("Save Info"):
        if name.strip() == "" or email.strip() == "" or usn.strip() == "":
            st.error("Please enter Name, USN, and Email")
        else:
            st.session_state["name"] = name
            st.session_state["usn"] = usn
            st.session_state["email"] = email
            st.success("Info saved! Click 'Start Capture' below to take images.")

    if "name" in st.session_state and "usn" in st.session_state and "email" in st.session_state:
        student_id = register_student(st.session_state["name"], st.session_state["email"], st.session_state["usn"])
        if student_id is not None:
            st.success(f"Student {st.session_state['name']} (USN: {st.session_state['usn']}) registered with ID {student_id}")
            del st.session_state["name"]
            del st.session_state["usn"]
            del st.session_state["email"]

# ---------------- Train Model ----------------
elif choice == "Train Model":
    st.markdown('<div class="card"><h2>Train Face Recognition Model</h2></div>', unsafe_allow_html=True)
    st.write("Train the face recognition model using captured student images.")
    if st.button("Train"):
        train_model()
        st.success("Model Trained Successfully")

# ---------------- Start Attendance ----------------
elif choice == "Start Attendance":
    st.markdown('<div class="card"><h2>Start Attendance</h2></div>', unsafe_allow_html=True)
    st.write("Starting Attendance. Press 'q' to stop.")
    recognize_faces()

# ---------------- Attendance Report ----------------
elif choice == "Attendance Report":
    st.markdown('<div class="card"><h2>Attendance Report</h2></div>', unsafe_allow_html=True)
    df_percentage = get_attendance_percentage()
    if df_percentage is not None:
        st.dataframe(df_percentage)
        csv = df_percentage.to_csv(index=False)
        st.download_button("Download CSV", csv, "attendance_percentage.csv", "text/csv")

# ---------------- Individual Attendance ----------------
elif choice == "Individual Attendance":
    st.markdown('<div class="card"><h2>Individual Attendance</h2></div>', unsafe_allow_html=True)
    df_percentage = get_attendance_percentage()
    if df_percentage is not None and not df_percentage.empty:
        search_input = st.text_input("Enter Student Name or USN to search")
        if search_input:
            student_data = df_percentage[
                (df_percentage['Name'].str.contains(search_input, case=False, na=False)) |
                (df_percentage['USN'].str.contains(search_input, case=False, na=False))
            ]
            if not student_data.empty:
                for _, student in student_data.iterrows():
                    st.subheader(f"{student['Name']} (USN: {student['USN']})")
                    st.write(f"Attendance %: {student['Attendance %']}%")
                    if student['Attendance Details'] != "No records":
                        st.markdown("**Dates & Times Attended:**")
                        for dt in student['Attendance Details'].split(", "):
                            st.write(f"- {dt}")
                    else:
                        st.info("No attendance records found for this student.")
            else:
                st.warning("No matching student found.")
    else:
        st.info("No attendance data available.")
