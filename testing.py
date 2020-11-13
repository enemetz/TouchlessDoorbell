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
    tokens = []
    tokens.append("python3")
    tokens.append("run.py")
    tokens.append("example/model.h5")
    tokens.append("token")
    tokens.append("token")
    tokens.append("token")
    tokens.append("token")
    startLive = subprocess.Popen(tokens, stdout=subprocess.PIPE)

if __name__ == "__main__":
    main()