
import logging as log
from collections import deque
from threading import Thread
from time import time
# from absl import app, flags, logging
# from absl.flags import FLAGS

import cv2


class CameraDump:
    """ Independent camera feed
    Uses threading to grab IP camera frames in the background
    :param camera_name: Name of the camera
    :param camera_uri: IP/RTSP/Webcam URI
    :param interval: seconds between dumps
    :param deque_size: Max size of the deque collection
    :type camera_name: str
    :type camera_uri: str
    :type interval: int
    :type deque_size: int
    """

    def __init__(self, camera_name, camera_uri, interval=2, deque_size=25):
        self.camera_name = camera_name

        # Initialize deque used to store frames from the stream
        self.deque = deque(maxlen=deque_size)

        # Implementation of timers
        self.dump_time = time()
        self.interval = interval

        # Intialize camer stream URI
        self.camera_stream_uri = camera_uri

        # Flag to check if camera is valid/working
        self.online = False
        self.capture = None
        self.video_frame = None

        self.load_network_stream()

        # Start frame dumping in the background
        self.frame_thread = Thread(target=self.get_frame, args=())
        self.frame_thread.daemon = True
        self.frame_thread.start()

        print(f"Started camera {self.camera_name}!")

    def load_network_stream(self):
        """Verifies stream link and open new stream if valid"""

        def load_network_stream_thread():
            if self.verify_network_stream(self.camera_stream_uri):
                self.capture = cv2.VideoCapture(self.camera_stream_uri)
                self.online = True
                print(f"Video stream {self.camera_name} created!")

        self.load_stream_thread = Thread(target=load_network_stream_thread, args=())
        self.load_stream_thread.daemon = True
        self.load_stream_thread.start()

    def verify_network_stream(self, uri):
        """Attempts to receive a frame from given URI"""
        cap = cv2.VideoCapture(uri)
        if not cap.isOpened():
            return False
        cap.release()
        return True

    def get_frame(self):
        """Reads frame from the stream"""
        while True:
            try:
                if self.capture.isOpened() and self.online:
                    # Read next frame from the stream and append into deque
                    status, frame = self.capture.read()
                    if status:
                        self.deque.append(frame)
                    else:
                        self.capture.release()
                        self.online = False
                else:
                    # Attempt to reconnect
                    log.info('Attempting to reconnect...', self.camera_stream_uri)
                    self.load_network_stream()
                    self.spin(2)
                self.spin(.001)
            except AttributeError:
                pass

    def spin(self, seconds):
        """Pause for set amount of seconds, currently time.sleep"""
        time_end = time() + seconds
        while time() < time_end:
            continue  # Replace in order not to stall the app

    def dump_frame(self):
        """Dumps frame on the disk"""
        if not self.online:
            self.spin(1)
            return None
        if self.deque and self.online and time() >= self.dump_time + self.interval:
            frame = self.deque[-1]
            self.dump_time = time()
            return frame
