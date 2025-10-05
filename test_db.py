from utils import create_connection

conn = create_connection()
if conn is not None:
    print("Connection successful!")
else:
    print("Failed to connect.")
