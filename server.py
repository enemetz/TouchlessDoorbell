import socket
import sys
import signal
import os
import subprocess
import liveStream
import picamera
import time
import datetime
import glob
from pathlib import Path



def main():

    # create the socket for the rs server
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[S]: Server socket created")
    except socket.error as err:
        print('[S]: socket open error: {}\n'.format(err))
        exit()

    # bind the socket to the port to listen for the client
    server_binding = ('', 9000)
    ss.bind(server_binding)
    ss.listen(5)
    host = socket.gethostname()
    print("[S]: Server host name is {}".format(host))
    localhost_ip = (socket.gethostbyname(host))
    print("[S]: Server IP address is {}".format(localhost_ip))
    
    
    startLive = ''
    isLive = False
    
    
    userAndTokens = {}

    startDetection = ''
    isArmed = False

    takeDetectPic = "YES"
    

    # get list of host names to check for
    while True:
        conn, addr = ss.accept()
        print("[S]: Got connection from: ", addr)
        length_of_message = int.from_bytes(conn.recv(2), byteorder='big')
        msg = conn.recv(length_of_message).decode("UTF-8")
        print("[S]: Message from client: " + msg)

        # Note the corrected indentation below
        if "StartLive" in msg:
            print("[S]: Starting Live Stream ...")
            
            if isArmed == True:
                startDetection.terminate()
                startDetection = ''
            
            if isLive == False:
                startLive = subprocess.Popen(["python3", "liveStream.py"], stdout=subprocess.PIPE)
                isLive = True
            
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
        elif "EndLive" in msg:
            print("[S]: Ending Live Stream ...")
            
            if isLive == True:
                startLive.terminate()
                startLive = ''
                isLive = False
            
            if isArmed == True:
                # gets args ready 
                args = []
                args.append("python3")
                args.append("run.py")
                args.append("example/model.h5")
                args.append(takeDetectPic)
            
                # append tokens
                for key, value in userAndTokens.items():
                    args.append(value)
                
                startDetection = subprocess.Popen(args, stdout=subprocess.PIPE)
                isArmed = True
            
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
        elif "Take Pic" in msg:
            print("[S]: Taking pic ...")
            
            if isLive == True:
                startLive.terminate()
                startLive = ''

            time.sleep(1)
            
            with picamera.PiCamera() as camera:
                now = datetime.datetime.now()
                dateAndTime = now.strftime("%Y-%m-%d %H:%M:%S")
                camera.resolution = (1280, 720)
                camera.capture(dateAndTime + ".jpg")  # will be saved in the current directory.
                camera.close()
                
            startLive = subprocess.Popen(["python3", "liveStream.py"], stdout=subprocess.PIPE)
            
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            
        elif "Send Pics" in msg:
            print("[S]: Sending pics ...")
            allCurrentPics = glob.glob("*.jpg")
            # print(len(allCurrentPics))
            
            # send number of pics to client
            message_to_send = str(len(allCurrentPics)).encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            
            # client: OK
            length_of_message = int.from_bytes(conn.recv(2), byteorder='big')
            msg = conn.recv(length_of_message).decode("UTF-8")
            print("[S]: Message from client: " + msg)
            
            
            # send all pics . . .
            for pic in allCurrentPics:
                print("[S]: Sending " + pic + " ...")
                message_to_send = pic.encode("UTF-8")
                conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
                conn.send(message_to_send)
                
                # OK from client
                length_of_message = int.from_bytes(conn.recv(2), byteorder='big')
                msg = conn.recv(length_of_message).decode("UTF-8")
                print("[S]: Message from client: " + msg)
                
                # send the size of the image to the client
                a = Path(pic).stat().st_size
                message_to_send = str(a).encode("UTF-8")
                conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
                conn.send(message_to_send)
                
                # OK from client
                length_of_message = int.from_bytes(conn.recv(2), byteorder='big')
                msg = conn.recv(length_of_message).decode("UTF-8")
                print("[S]: Message from client: " + msg)
                
                picToSend = open(pic,'rb')
                while (True):
                    picPtr = picToSend.read(1024)
                    if not picPtr:
                        break
                    conn.sendall(picPtr)
                print("[S]: Removing " + pic)
                os.remove(pic)
                
                # OK from client
                length_of_message = int.from_bytes(conn.recv(2), byteorder='big')
                msg = conn.recv(length_of_message).decode("UTF-8")
                print("[S]: Message from client: " + msg)
                
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            conn.close()
            
        elif "Log In" in msg:
            # need to get username and token
            print("[S]: Getting username and token ...")
            
            # send OK
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            
            # client: Username
            length_of_message = int.from_bytes(conn.recv(2), byteorder='big')
            msg = conn.recv(length_of_message).decode("UTF-8")
            print("[S]: Message from client: " + msg)
            user = msg
            
            # send OK
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            
            # client: token
            length_of_message = int.from_bytes(conn.recv(2), byteorder='big')
            msg = conn.recv(length_of_message).decode("UTF-8")
            print("[S]: Message from client: " + msg)
            token = msg
            
            # add this (user:token) pair to the dictionary
            userAndTokens[user] = token
            
            print("[S]: Current Users + Tokens: ")
            print(userAndTokens)
            
            if isArmed == True:
                startDetection.terminate()
                startDetection = ''
                
                # gets args ready 
                args = []
                args.append("python3")
                args.append("run.py")
                args.append("example/model.h5")
                args.append(takeDetectPic)
            
                # append tokens
                for key, value in userAndTokens.items():
                    args.append(value)
            
                # arm the camera
                startDetection = subprocess.Popen(args, stdout=subprocess.PIPE)
                isArmed = True
            
            # send OK
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
        elif "Arm Doorbell" in msg:
            print("[S]: Arming Doorbell ...")
            
            # gets args ready 
            args = []
            args.append("python3")
            args.append("run.py")
            args.append("example/model.h5")
            args.append(takeDetectPic)
            
            # append tokens
            for key, value in userAndTokens.items():
                args.append(value)
            
            # arm the camera
            if isArmed == False:
                startDetection = subprocess.Popen(args, stdout=subprocess.PIPE)
                isArmed = True
            
            # send OK
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            
        elif "Disarm Doorbell" in msg:
            print("[S]: Disarming Doorbell ...")
            
            if isArmed == True:
                startDetection.terminate()
                startDetection = ''
                isArmed = False
            
            # send OK
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            
        elif "Stop Notifications" in msg:
            # send OK
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            
            # client: Username
            length_of_message = int.from_bytes(conn.recv(2), byteorder='big')
            msg = conn.recv(length_of_message).decode("UTF-8")
            print("[S]: Message from client: " + msg)
            user = msg
            
            print("[S]: Getting rid of token for " + user + " ...")
            
            if user in userAndTokens:
                userAndTokens.pop(user)
            
            if isArmed == True:
                startDetection.terminate()
                startDetection = ''
                
                # gets args ready 
                args = []
                args.append("python3")
                args.append("run.py")
                args.append("example/model.h5")
                args.append(takeDetectPic)
            
                # append tokens
                for key, value in userAndTokens.items():
                    args.append(value)
            
                # arm the camera
                startDetection = subprocess.Popen(args, stdout=subprocess.PIPE)
                isArmed = True
                
            # send OK
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            conn.close()

        elif "Send Notifs" in msg:
            print("[S]: Sending notifications ...")
            allCurrentPics = glob.glob("*.txt")
            # print(len(allCurrentPics))
            
            # send number of pics to client
            message_to_send = str(len(allCurrentPics)).encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            
            # client: OK
            length_of_message = int.from_bytes(conn.recv(2), byteorder='big')
            msg = conn.recv(length_of_message).decode("UTF-8")
            print("[S]: Message from client: " + msg)
            
            
            # send all pics . . .
            for pic in allCurrentPics:
                print("[S]: Sending " + pic + " ...")
                message_to_send = pic.encode("UTF-8")
                conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
                conn.send(message_to_send)
                
                # OK from client
                length_of_message = int.from_bytes(conn.recv(2), byteorder='big')
                msg = conn.recv(length_of_message).decode("UTF-8")
                print("[S]: Message from client: " + msg)
                
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            conn.close()
            
        elif "Pic Capture ON" in msg:
            print("[S]: Turning picture capture on...")
            takeDetectPic = "YES"

            # if the camera is armed, disarm it and then start it with pic capture on  
            if isArmed == True:
                startDetection.terminate()
                startDetection = ''
                
                # gets args ready 
                args = []
                args.append("python3")
                args.append("run.py")
                args.append("example/model.h5")
                args.append(takeDetectPic)
            
                # append tokens
                for key, value in userAndTokens.items():
                    args.append(value)
            
                # arm the camera
                startDetection = subprocess.Popen(args, stdout=subprocess.PIPE)
                isArmed = True

            # send OK back
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            conn.close()

        elif "Pic Capture OFF" in msg:
            print("[S]: Turning picture capture off...")
            takeDetectPic = "NO"

            # if the camera is armed, disarm it and then start it with pic capture on  
            if isArmed == True:
                startDetection.terminate()
                startDetection = ''
                
                # gets args ready 
                args = []
                args.append("python3")
                args.append("run.py")
                args.append("example/model.h5")
                args.append(takeDetectPic)
            
                # append tokens
                for key, value in userAndTokens.items():
                    args.append(value)
            
                # arm the camera
                startDetection = subprocess.Popen(args, stdout=subprocess.PIPE)
                isArmed = True

            # send OK back
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            conn.close()
        
        elif "Delete Notifs" in msg:
            print("[S]: Deleting notifications ...")
            
            # send OK
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)

            # client: number of notifications to delete
            length_of_message = int.from_bytes(conn.recv(2), byteorder='big')
            msg = conn.recv(length_of_message).decode("UTF-8")
            print("[S]: Message from client: " + msg)

            # send OK
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)

            numNotifsToDelete = int(msg)
            count = 1;
            while count <= numNotifsToDelete:
                # client: file to delete
                length_of_message = int.from_bytes(conn.recv(2), byteorder='big')
                msg = conn.recv(length_of_message).decode("UTF-8")
                print("[S]: File to delete: " + msg)
                
                if os.path.exists(msg):
                    os.remove(msg)
                    print("[S]: " + msg + " deleted")
                
                # send OK
                message_to_send = "OK".encode("UTF-8")
                conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
                conn.send(message_to_send)

                count = count + 1

            conn.close()
        else:
            print("[S]: Sending test...")
            message_to_send = "TEST".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            conn.close()
            

    # Close the server socket
    ss.close()
    exit()


if __name__ == "__main__":
    main()
