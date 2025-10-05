import cv2

# Load Haar cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Check if file is loaded correctly
print("Is Haar cascade loaded correctly?", not face_cascade.empty())
