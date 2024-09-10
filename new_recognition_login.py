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

import cv2
import numpy as np
from sahi import AutoDetectionModel
from sahi.predict import get_prediction

yolo_model_path, yolo_version = ("best.pt", "yolov5")

HOD_MAIL = "aftabsab98807@gmail.com" #Change HOD mail here

ADVANCE = 0
DEBUG = 1

detection_model = AutoDetectionModel.from_pretrained(
    model_type= yolo_version,
    model_path=yolo_model_path,
    confidence_threshold=0.5,
    device="cpu", # or 'cuda:0'
)

DATA_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'shared_data/')

window_name = "Shared_FaceRecog"

KNOWN_FACES_DIR = 'face_data'
TOLERANCE = 0.4
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = 'hog'

count = 0
start = time.time() + 1

f1 = open("./files/camera_resolution.txt", "r")
res_data = f1.read().strip()
f1.close()
res_data = res_data.split(",")
divide_factor = int(res_data[1]) // 240
image_resolution = (int(res_data[0])//divide_factor, int(res_data[1])//divide_factor)


while True:
    try:
        shared_image = shared_memory.SharedMemory(name='shared_raw_image')
        raw_image = np.ndarray((image_resolution[1], image_resolution[0], 3), dtype=np.uint8, buffer=shared_image.buf)
        break
    except:
        print("Waiting for Shared Camera Stream")
        time.sleep(2)

print(raw_image.nbytes, raw_image.shape, raw_image.dtype)
try:
    shared_processed_image = shared_memory.SharedMemory(create=True, size=raw_image.nbytes, name="shared_processed_image")
except FileExistsError:
    shared_processed_image = shared_memory.SharedMemory(create=False, size=raw_image.nbytes, name="shared_processed_image")
    shared_processed_image.unlink()

    time.sleep(2)
    shared_processed_image = shared_memory.SharedMemory(create=True, size=raw_image.nbytes, name="shared_processed_image")

processed_image_buf = np.ndarray(raw_image.shape, dtype=raw_image.dtype, buffer=shared_processed_image.buf)

print('Loading known faces...', end =" ")
try:
    known_faces = np.load('./files/known_faces.npy', allow_pickle=True).tolist()
    known_names = np.load('./files/known_names.npy', allow_pickle=True).tolist()
except FileNotFoundError:
    ls = []
    np.save('./files/known_faces', np.array(ls))
    np.save('./files/known_names', np.array(ls))

f1 = open("./files/face_data_change.txt", 'w')
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
yolo_res = None
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


        result = get_prediction(image_rgb, detection_model)
        yolo_res = result.to_coco_annotations()

        if DEBUG:
            print("Objects Detected:", len(yolo_res))

        img = np.array(result.image)

        all_names = []
        id_detected = False
        for detection in yolo_res:
            bbox = detection['bbox']
            conf = detection['score']
            cls = detection['category_id']
            name = detection['category_name']
            area = detection['area']
            iscrowd = detection['iscrowd']

            start_point = (int(bbox[0]), int(bbox[1]))
            end_point = (int(bbox[0]+bbox[2]), int(bbox[1]+bbox[3]))

            all_names.append(name)

            if "tag" in name:
                id_detected = True

            # color = (100,100,0)
            # thickness = 2
            # image = cv2.rectangle(image, start_point, end_point, color, thickness)
            # cv2.putText(image, str(name)+" "+str(conf)[:4],start_point, cv2.FONT_HERSHEY_PLAIN, 1, (50,50,200), 2)

        print("All Objects Detected by Yolo:", all_names)

        

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
                if len(attendance) == 0:
                    print("Adding Attendance to Database")
                    conn.execute(f"INSERT INTO ATTENDANCE (ID, NAME, BRANCH, DAY, MONTH, YEAR, LOGIN_TIME) \
                        VALUES ('{match}', '{users_data[match][0]}' , '{users_data[match][1]}', '{day}', '{month}', '{year}', '{in_time}') ")
                    conn.commit()
                    conn.close()

                    if hour > late_hour and minute > late_minute:
                        print("Let Coming Student")
                        sendmail(None, subject=f"Late Incoming Student:{users_data[match][0]}", message= f"The following Student Came Late: {users_data[match][0]}",
                                  to=HOD_MAIL )
                        
                if not id_detected:
                    print("Student Without ID Card Detected")
                    cv2.imwrite("./files/last.png", raw_image)
                    sendmail("./files/last.png", subject=f"Student Detected without ID Card:{users_data[match][0]}", message= f"The following Student was detected without ID Card: {users_data[match][0]}",
                                to=HOD_MAIL )

                


            else:
                faces.append(['Unknown', face_location])
                f1 = open(DATA_FOLDER+"speak_greetings.txt", "a")
                f1.write("Unknown\n")
                f1.close()
    else:
        status = 0


    if face_detected:
        #print("Face was detected")

        all_names = []
        for detection in yolo_res:
            bbox = detection['bbox']
            conf = detection['score']
            cls = detection['category_id']
            name = detection['category_name']
            area = detection['area']
            iscrowd = detection['iscrowd']

            start_point = (int(bbox[0]), int(bbox[1]))
            end_point = (int(bbox[0]+bbox[2]), int(bbox[1]+bbox[3]))

            all_names.append(name)

            color = (100,100,0)
            thickness = 2
            image = cv2.rectangle(image, start_point, end_point, color, thickness)
            cv2.putText(image, str(name)+" "+str(conf)[:4],start_point, cv2.FONT_HERSHEY_PLAIN, 1, (50,50,200), 2)

        print("All Objects Detected by Yolo:", all_names)

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
        f1 = open("./files/face_data_change.txt", 'r')
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


