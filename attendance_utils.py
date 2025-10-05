import pandas as pd
import streamlit as st
from utils import create_connection

def get_attendance_percentage():
    """
    Returns a Streamlit-friendly DataFrame with:
    - Student ID
    - Name
    - USN
    - Attendance %
    - Attendance Details (date + time)
    """
    conn = create_connection()
    if conn is None:
        st.error("Database connection failed")
        return None

    # Fetch students and attendance from DB
    students_df = pd.read_sql("SELECT * FROM students", conn)
    attendance_df = pd.read_sql("SELECT * FROM attendance", conn)

    if students_df.empty:
        st.warning("No students found in the database")
        return pd.DataFrame()

    # Total distinct days (for calculating percentage)
    total_days = attendance_df['date'].nunique() if not attendance_df.empty else 0

    result = []
    for _, student in students_df.iterrows():
        student_id = student['student_id']
        student_attendance = attendance_df[attendance_df['student_id'] == student_id].copy()
        present_days = student_attendance['date'].nunique() if not student_attendance.empty else 0
        percentage = (present_days / total_days) * 100 if total_days > 0 else 0

        # Format attendance details: "YYYY-MM-DD HH:MM:SS"
        if not student_attendance.empty:
            student_attendance['datetime'] = student_attendance['date'].astype(str) + " " + student_attendance['time'].astype(str)
            attendance_details_str = ", ".join(student_attendance['datetime'].tolist())
        else:
            attendance_details_str = "No records"

        result.append({
            "Student ID": student_id,
            "Name": student['name'],
            "USN": student['usn'],
            "Attendance %": round(percentage, 2),
            "Attendance Details": attendance_details_str
        })

    df_percentage = pd.DataFrame(result)

    return df_percentage
 