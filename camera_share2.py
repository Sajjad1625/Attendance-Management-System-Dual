import cv2
import numpy as np
from multiprocessing import shared_memory
import time
import os

# from imutils.video import VideoStream
# os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

try:
    f1 = open("./files/camera_source2.txt", "r")
    text_data = f1.read()
    f1.close()
    try:
        
        cam_source = int(text_data)
    except:
        cam_source = text_data
    
except Exception as e:
    print("Unable to Camera Source, Using Default Camera.")
    cam_source = 0

def share_stream():
    print('Initializing Camera')
    print("OpenCV Mode:", cam_source)
    if ":/" in str(cam_source):
        print("Network Mode")
        cap = cv2.VideoCapture(cam_source)
    else:
        print("Webcam Mode")
        cap = cv2.VideoCapture(cam_source)#,cv2.CAP_DSHOW)
    

    print('Waiting for First Frame')
    raw_imag = None
    while raw_imag is None:
        _,raw_imag = cap.read()
        time.sleep(0.1)
    print('Got First Frame')

    print("Raw Camera Resolution: ", raw_imag.nbytes, raw_imag.shape)
    f1 = open("./files/camera_resolution2.txt", "w")
    f1.write(str(raw_imag.shape[1]) + "," + str(raw_imag.shape[0]))
    f1.close()

    f1 = open("./files/camera_resolution2.txt", "r")
    res_data = f1.read().strip()
    f1.close()
    res_data = res_data.split(",")
    divide_factor = int(res_data[1]) // 240
    image_resolution = (int(res_data[0])//divide_factor, int(res_data[1])//divide_factor)

    raw_image = cv2.resize(raw_imag, image_resolution)
    print(raw_image.nbytes, raw_image.shape, raw_image.dtype)

    try:
        shared_image = shared_memory.SharedMemory(create=True, size=raw_image.nbytes, name="shared_raw_image2")
    except FileExistsError:
        shared_image = shared_memory.SharedMemory(create=False, size=raw_image.nbytes, name="shared_raw_image2")
        shared_image.unlink()

        time.sleep(2)
        shared_image = shared_memory.SharedMemory(create=True, size=raw_image.nbytes, name="shared_raw_image2")

    raw_image_buf = np.ndarray(raw_image.shape, dtype=raw_image.dtype, buffer=shared_image.buf)

    print("Started Sharing Stream 2 through: ", shared_image.name)

    start = time.time()
    count = 0

    while True:
        _,raw_imag = cap.read()
        
        if raw_imag is not None:
            raw_image = cv2.resize(raw_imag, image_resolution)
            # cv2.imshow("Frame", raw_image)
            raw_image_buf[:] = raw_image[:]
            if (cv2.waitKey(20) == 113):
                break

        count += 1
        if time.time() - start >= 10:
            fps = count/10
            print("Average FPS: ", fps )
            if fps < 5:
                print("Very Low FPS, Consider using a better Camera & more Powerful PC")
            count = 0
            start = time.time()


share_stream()        
