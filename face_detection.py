import io
import picamera
import cv2
import numpy
import time
from sys import argv, stderr, exit
from os import getenv
import datetime
import FCMManager


i = 1
tokens = []
while i < len(argv):
    tokens.append(argv[i])
    i = i + 1


while True:
    while True:
        print("starting...")
        stream = io.BytesIO()
        camera = picamera.PiCamera()
        camera.resolution = (1280,720)
        camera.capture(stream, format='jpeg')
        
        #Convert the picture into a numpy array
        buff = numpy.frombuffer(stream.getvalue(), dtype=numpy.uint8)

        #Now creates an OpenCV image
        image = cv2.imdecode(buff, 1)

        #https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
        #Load a cascade file for detecting faces
        face_cascade = cv2.CascadeClassifier('/home/pi/Desktop/TouchlessDoorbell/haarcascade_frontalface_default.xml')
        
        #Convert to grayscale
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

        #Look for faces in the image using the loaded cascade file
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    
        if len(faces) > 0:
            print("Face detected ...")
            break
        
        camera.close()
    
    # send notification
    if len(tokens) > 0:
        print("Sending Notification ...")
        FCMManager.send("Doorbell activated!", "Someone is at the door", tokens)
        
    now = datetime.datetime.now()
    dateAndTime = now.strftime("%Y-%m-%d %H:%M:%S")
    cv2.imwrite(dateAndTime + ".jpg",image)
    camera.close()
    time.sleep(8)
    


'''
/home/pi/Desktop/TouchlessDoorbell/
'''


