import cv2
import time
import datetime
import pymongo
from pymongo import MongoClient
from gridfs import GridFS
import os

client = MongoClient("mongodb+srv://Mvacc:pwd@iotproject.lkfss1w.mongodb.net/?retryWrites=true&w=majority")
db = client.your_database_name
fs = GridFS(db)

cap = cv2.VideoCapture(0)

# Load the cascade to detect faces and bodies
face_cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(face_cascade_path)

body_cascade_path = cv2.data.haarcascades + "haarcascade_fullbody.xml"
body_cascade = cv2.CascadeClassifier(body_cascade_path)

detection = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5

# Set the frame size to the size of the camera frame
frameSize = (int(cap.get(3)), int(cap.get(4)))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

video_save_directory = "C:/Users/Mvacc/OneDrive/Documents/Semester 7/IOT 2/SecurityCamera2/static/video"
# Store the recroded video in GridFS
def store_video_in_gridfs(file_path, metadata):
    with open(file_path, 'rb') as f:
        contents = f.read()
        video_id = fs.put(contents, filename=file_path, metadata=metadata)
    return video_id

# Use an infinite loop to repeatedly read frames from the camera
while True:
    _, frame = cap.read()


    # Convert frames recorded by camera to grayscale to detect faces and bodies using Haar Cascade
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces and bodies
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    bodies = body_cascade.detectMultiScale(gray, 1.3, 5)

    # Draw a purple rectangle around faces and bodies
    for (x, y, width, height) in faces:
        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 255), 3)

    if len(faces) + len(bodies) > 0:
        # If detection is already detecting movement, then set the timer to false
        if detection:
            timer_started = False

        # If detection has just started, then update the timer with the current time
        else:
            detection = True
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            video_filename = f"{current_time}.mp4"
            video_filename2 = video_save_directory + f"{current_time}.mp4"
            out = cv2.VideoWriter(video_filename2, fourcc, 15, frameSize)
            print("Started Recording!")
            start_time = datetime.datetime.now()

    # If no faces or bodies are detected run these statements
    elif detection:
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False
                out.release()
                print("Stopped Recording")
                end_time = datetime.datetime.now()

                # Store video in GridFS
                metadata = {
                    "start_time": start_time.strftime("%d-%m-%Y-%H-%M-%S"),
                    "end_time": end_time.strftime("%d-%m-%Y-%H-%M-%S"),
                    "duration": str(end_time - start_time)
                }
                # Store the video in GridFS
                video_id = store_video_in_gridfs(video_filename, metadata)
                print(f"Video stored in GridFS with ID: {video_id}")
        else:
            timer_started = True
            detection_stopped_time = time.time()
    
    if detection:
        out.write(frame)

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) == ord('q'):
        break

out.release()
cap.release()
cv2.destroyAllWindows()
