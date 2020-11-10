import socket
import sys
import signal
import os
import subprocess
import liveStream
import picamera
import time
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
            
            startLive = subprocess.Popen(["python3", "liveStream.py"], stdout=subprocess.PIPE)
            
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
        elif "EndLive" in msg:
            print("[S]: Ending Live Stream ...")
            
            startLive.terminate()
            
            
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
        elif "Take Pic" in msg:
            print("[S]: Taking pic ...")
            
            startLive.terminate()
            time.sleep(1)
            
            with picamera.PiCamera() as camera:
                dateAndTime = time.asctime( time.localtime(time.time()) )
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
                os.remove(pic)
                
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
            conn.close()
            
        else:
            print("[S]: Do nothing")
            conn.close()
            

    # Close the server socket
    ss.close()
    exit()


if __name__ == "__main__":
    main()
