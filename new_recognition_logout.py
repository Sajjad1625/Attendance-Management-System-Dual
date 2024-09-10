import numpy as np
import cv2
import os
from multiprocessing import shared_memory
from threading import Thread
import face_recognition
import time
import sqlite3
from datetime import datetime

from mailsend import sendmail

DATA_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'shared_data/')

window_name = "Shared_FaceRecog"

KNOWN_FACES_DIR = 'face_data'
TOLERANCE = 0.4
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = 'hog'

count = 0
start = time.time() + 1

f1 = open("./files/camera_resolution2.txt", "r")
res_data = f1.read().strip()
f1.close()
res_data = res_data.split(",")
divide_factor = int(res_data[1]) // 240
image_resolution = (int(res_data[0])//divide_factor, int(res_data[1])//divide_factor)


while True:
    try:
        shared_image = shared_memory.SharedMemory(name='shared_raw_image2')
        raw_image = np.ndarray((image_resolution[1], image_resolution[0], 3), dtype=np.uint8, buffer=shared_image.buf)
        break
    except:
        print("Waiting for Shared Camera Stream")
        time.sleep(2)

print(raw_image.nbytes, raw_image.shape, raw_image.dtype)
try:
    shared_processed_image = shared_memory.SharedMemory(create=True, size=raw_image.nbytes, name="shared_processed_image2")
except FileExistsError:
    shared_processed_image = shared_memory.SharedMemory(create=False, size=raw_image.nbytes, name="shared_processed_image2")
    shared_processed_image.unlink()

    time.sleep(2)
    shared_processed_image = shared_memory.SharedMemory(create=True, size=raw_image.nbytes, name="shared_processed_image2")

processed_image_buf = np.ndarray(raw_image.shape, dtype=raw_image.dtype, buffer=shared_processed_image.buf)

print('Loading known faces...', end =" ")
try:
    known_faces = np.load('./files/known_faces.npy', allow_pickle=True).tolist()
    known_names = np.load('./files/known_names.npy', allow_pickle=True).tolist()
except FileNotFoundError:
    ls = []
    np.save('./files/known_faces', np.array(ls))
    np.save('./files/known_names', np.array(ls))

f1 = open("./files/face_data_change2.txt", 'w')
f1.close()

conn = sqlite3.connect('./files/data.db')
cursor = conn.execute("SELECT NAME, ID, BRANCH, MESSAGE, MAIL_ID, PARENT_NAME, PARENT_MAIL from USER")
users_data = dict()
for row in cursor:
    users_data[row[1]] = (row[0], row[2], row[3])
conn.close()

print("Loaded")

day = datetime.now().day
month = datetime.now().month
year = datetime.now().year
hh = datetime.now().hour
mm = datetime.now().minute

# print("Datetime: ", day, month, year, hh, mm)
# print("Known Names: ", known_names)
# print("Users Data:",users_data)

status = 0
while True:
    
    # cv2.imshow(window_name, raw_image)

    day = datetime.now().day
    month = datetime.now().month
    year = datetime.now().year
    hour = datetime.now().hour
    minute = datetime.now().minute
    in_time = str(hour)+":"+str(minute) 

    
    f1 = open("./files/late_time.txt")
    late_data = f1.read()
    f1.close()

    late_data = late_data.split(",")
    late_hour = int(late_data[0])
    late_minute = int(late_data[1])

    image = raw_image.copy()

    if status == 0:
        status = 1
        image_rgb = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)

        locations = face_recognition.face_locations(image_rgb, model=MODEL)
        encodings = face_recognition.face_encodings(image_rgb, locations)
        face_detected = False
        faces = []
        
        for face_encoding, face_location in zip(encodings, locations):
            results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
            face_detected = True
            match = None
            if True in results:
                match = known_names[results.index(True)]

                f1 = open(DATA_FOLDER+"speak_greetings.txt", "a")
                f1.write(match+"\n")
                f1.close()
            
                faces.append([ users_data[match][0], face_location])
                conn = sqlite3.connect('./files/data.db')
                cursor = conn.execute(f"SELECT NAME from ATTENDANCE where ID = '{match}' AND DAY = '{day}' AND MONTH = '{month}' AND YEAR = '{year}'; ")
                attendance = []
                for row in cursor:
                    attendance.append(row)
                if len(attendance) != 0:
                    print("Adding Logout Attendance to Database")
                    conn.execute(f"UPDATE ATTENDANCE set LOGOUT_TIME = '{in_time}' where ID = '{match}' AND DAY = '{day}' AND MONTH = '{month}' AND YEAR = '{year}' ;")
                    conn.commit()
                else:
                    print("Detected Logout without Login for:", match)

                    
                conn.close()


            else:
                faces.append(['Unknown', face_location])
                f1 = open(DATA_FOLDER+"speak_greetings.txt", "a")
                f1.write("Unknown\n")
                f1.close()
    else:
        status = 0


    if face_detected:
        #print("Face was detected")
        for name, face_location in faces:

            color = [(ord(c.lower()) - 97) * 8 for c in name[:3]]
            top_left = (face_location[3], face_location[0])
            bottom_right = (face_location[1], face_location[2])
            cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)
            
            top_left = (face_location[3]-2, face_location[0]-22)
            bottom_right = (face_location[1]+2, face_location[0])
            cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
            cv2.putText(image, name, (face_location[3] + 10, face_location[0] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200,200), FONT_THICKNESS)

    processed_image_buf[:] = image[:]

    # cv2.imshow(window_name, image)
    cv2.waitKey(1)
    count += 1
    if time.time() - start >= 10:
        fps = count/10
        print("Average FPS: ", fps)
        if fps < 5:
            print("Very Low FPS, Consider using more Powerful PC")
        f1 = open("./files/face_data_change2.txt", 'r')
        face_data_change = f1.read()
        f1.close()
        if "1" in face_data_change:
            print("Face Data Changed")
            print('Loading known faces...', end =" ")
            known_faces = np.load('./files/known_faces.npy', allow_pickle=True).tolist()
            known_names = np.load('./files/known_names.npy', allow_pickle=True).tolist()
            f1 = open("./files/face_data_change.txt", 'w')
            f1.close()
            conn = sqlite3.connect('./files/data.db')
            cursor = conn.execute("SELECT NAME, ID, BRANCH, MESSAGE, MAIL_ID, PARENT_NAME, PARENT_MAIL from USER")
            users_data = dict()
            for row in cursor:
                users_data[row[1]] = (row[0], row[2], row[3])
            conn.close()
            print("Loaded")
        count = 0
        start = time.time()


