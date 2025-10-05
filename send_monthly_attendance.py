import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils import create_connection
import pandas as pd

def send_monthly_attendance():
    conn = create_connection()
    if conn is None:
        print("DB connection failed")
        return

    df = pd.read_sql("SELECT * FROM students", conn)
    attendance_df = pd.read_sql("SELECT * FROM attendance", conn)
    
    result = []
    for _, student in df.iterrows():
        student_id = student['student_id']
        total_days = attendance_df['date'].nunique()
        present_days = attendance_df[attendance_df['student_id'] == student_id]['date'].nunique()
        percentage = (present_days / total_days) * 100 if total_days > 0 else 0
        result.append({
            "name": student['name'],
            "email": student['email'],
            "percentage": round(percentage, 2)
        })

    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"  # Use app password for Gmail

    for student in result:
        receiver_email = student['email']
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = "Monthly Attendance Report"

        body = f"Hello {student['name']},\n\nYour attendance for this month is {student['percentage']}%.\n\nBest regards,\nAdmin"
        message.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()
            print(f"Sent to {student['name']}")
        except Exception as e:
            print(f"Failed to send to {student['name']}: {e}")

if __name__ == "__main__":
    send_monthly_attendance()
