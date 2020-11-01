import socket
import sys
import signal
import os
import subprocess
import liveStream



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
            #liveStream.main()
            
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
        elif "EndLive" in msg:
            print("[S]: Ending Live Stream ...")
            
            startLive.terminate()
            
            
            message_to_send = "OK".encode("UTF-8")
            conn.send(len(message_to_send).to_bytes(2, byteorder='big'))
            conn.send(message_to_send)
        else:
            print("[S]: Do nothing")
            

    # Close the server socket
    ss.close()
    exit()


if __name__ == "__main__":
    main()
