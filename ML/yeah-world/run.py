# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Run a trained model on frames from the camera and play random sounds when
class 0 is detected.
"""
from __future__ import print_function

from sys import argv, stderr, exit
from os import getenv

import numpy as np
from tensorflow import keras
import picamera
import time

from camera import Camera
from pinet import PiNet
from randomsound import RandomSound

# Smooth out spikes in predictions but increase apparent latency. Decrease on a Pi Zero.
SMOOTH_FACTOR = 0.8

SHOW_UI = getenv("DISPLAY")

if SHOW_UI:
    import pygame


def main():
    if len(argv) != 3 or argv[1] == '--help':
        print("""Usage: run.py MODEL token
Use MODEL to classify camera frames and play sounds when class 0 is recognised.""")
        exit(1)

    model_file = argv[1]
    
    print(argv[2])
    
    # We use the same MobileNet as during recording to turn images into features
    print('Loading feature extractor')
    extractor = PiNet()

    # Here we load our trained classifier that turns features into categories
    print('Loading classifier')
    classifier = keras.models.load_model(model_file)

    # Initialize the camera and sound systems
    camera = Camera(training_mode=False)
    #random_sound = RandomSound()

    # Smooth the predictions to avoid interruptions to audio
    smoothed = np.ones(classifier.output_shape[1:])
    smoothed /= len(smoothed)

    print('Now running!')
    while True:
        while True:
            raw_frame = camera.next_frame()

            # Use MobileNet to get the features for this frame
            z = extractor.features(raw_frame)

            # With these features we can predict a 'normal' / 'yeah' class (0 or 1)
            # Keras expects an array of inputs and produces an array of outputs
            classes = classifier.predict(np.array([z]))[0]

            # smooth the outputs - this adds latency but reduces interruptions
            smoothed = smoothed * SMOOTH_FACTOR + classes * (1.0 - SMOOTH_FACTOR)
            selected = np.argmax(smoothed) # The selected class is the one with highest probability

            # Show the class probabilities and selected class
            summary = 'Class %d [%s]' % (selected, ' '.join('%02.0f%%' % (99 * p) for p in smoothed))
            stderr.write('\r' + summary)

            # Perform actions for selected class. In this case, play a sound from the sounds/ dir
            if selected == 0:
                print("Detected")
                break
        # hand detected, send notifcation
        dateAndTime = time.asctime( time.localtime(time.time()) )
        camera.camera.resolution = (1280,720)
        camera.camera.capture(dateAndTime + ".jpg")
        camera.camera.resolution = (128, 128)
        time.sleep(2)
        
            
        
if __name__ == '__main__':
    main()
