import cv2
import time
import datetime
from pymongo import MongoClient
from gridfs import GridFS
import os

# MongoDB Connection
client = MongoClient("mongodb+srv://Mvacc:pwd@iotproject.lkfss1w.mongodb.net/?retryWrites=true&w=majority")
db = client.your_database_name
fs = GridFS(db)

# Video Capture Setup
cap = cv2.VideoCapture(0)

# Cascade Classifiers for Face and Body Detection
face_cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(face_cascade_path)
body_cascade_path = cv2.data.haarcascades + "haarcascade_fullbody.xml"
body_cascade = cv2.CascadeClassifier(body_cascade_path)

# Detection Parameters
detection = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5
frameSize = (int(cap.get(3)), int(cap.get(4)))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

# Local Directory for Saving Videos
video_save_directory = "C:\\Users\\Mvacc\\OneDrive\\Documents\\Semester 7\\IOT 2\\SecurityCamera2\\static\\video"
if not os.path.exists(video_save_directory):
    os.makedirs(video_save_directory)

def store_video_in_gridfs(file_path, metadata):
    with open(file_path, 'rb') as f:
        contents = f.read()
        video_id = fs.put(contents, filename=os.path.basename(file_path), metadata=metadata)
    return video_id

while True:
    _, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    bodies = body_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, width, height) in faces:
        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 255), 3)

    if len(faces) + len(bodies) > 0:
        if not detection:
            detection = True
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            video_filename = f"{current_time}.mp4"
            video_full_path = os.path.join(video_save_directory, video_filename)
            out = cv2.VideoWriter(video_full_path, fourcc, 15, frameSize)
            print("Started Recording!")
            start_time = datetime.datetime.now()

    elif detection:
        if timer_started and time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
            detection = False
            timer_started = False
            out.release()
            print(f"Stopped Recording. Video saved at {video_full_path}")

            metadata = {
                "start_time": start_time.strftime("%d-%m-%Y-%H-%M-%S"),
                "end_time": datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S"),
                "duration": str(datetime.datetime.now() - start_time)
            }
            video_id = store_video_in_gridfs(video_full_path, metadata)
            print(f"Video stored in GridFS with ID: {video_id}")
        elif not timer_started:
            timer_started = True
            detection_stopped_time = time.time()

    if detection:
        out.write(frame)

    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
