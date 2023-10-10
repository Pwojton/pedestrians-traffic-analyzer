import argparse
import json
import logging as log
from pathlib import Path
from datetime import datetime
from collections import deque
from threading import Thread
from time import time

import cv2


class CameraDump:
    """ Independent camera feed
    Uses threading to grab IP camera frames in the background
    :param camera_name: Name of the camera
    :param dump_path: Path where frames are dumped
    :param camera_uri: IP/RTSP/Webcam URI
    :param interval: seconds between dumps
    :param deque_size: Max size of the deque collection
    :type camera_name: str
    :type dump_path: str
    :type camera_uri: str
    :type interval: int
    :type deque_size: int
    """

    def __init__(self, camera_name, dump_path='./data', camera_uri=0, interval=5, deque_size=1):
        self.camera_name = camera_name
        self.dump_path = dump_path

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

    def create_dump_dir(self):
        """Creates all subdirectories for dumped frames from cameras
        :return: Current path for the frames with yyyy-mm-dd as subdirectory
        :rtype: Path
        """
        current_date = datetime.now()
        path = Path(self.dump_path).joinpath(self.camera_name,
                                             f"{current_date.year}-{current_date.month}-{current_date.day}")
        Path(path).mkdir(parents=True, exist_ok=True)
        return path

    def dump_frame(self):
        """Dumps frame on the disk"""
        if not self.online:
            self.spin(1)
            return
        if self.deque and self.online and time() >= self.dump_time + self.interval:
            # Grab the last frame
            frame = self.deque[-1]

            path = self.create_dump_dir()
            frame_filename = f"{time()}.png"
            cv2.imwrite(path.joinpath(frame_filename).as_posix(), frame)
            self.dump_time = time()
            print(f"Frame named {frame_filename} has been saved!")


if __name__ == "__main__":
    log.basicConfig(format='%(asctime)-15s::%(levelname)s::%(funcName)s::%(message)s', level=log.INFO,
                    handlers=[log.StreamHandler()])
    # handlers=[log.FileHandler('log/camera_dump.log'), log.StreamHandler()])
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='config_file', type=str, help="JSON config file")
    args = parser.parse_args()
    config = json.loads(open(args.config_file).read())
    if config:
        # Read all the parameters from config
        # protocol = config['protocol']
        dump_path = config['dump_path']
        cameras = config['cameras']
        log.info("Config file loaded!")
        camera_dumps = []
        for camera in cameras:
            if camera['dump']:
                camera_name = camera['name']
                interval = camera['interval']
                video_uri = f"http://live.uci.agh.edu.pl/video/stream2.cgi?start=1572349755"
                camera_dumps.append(CameraDump(camera_name, dump_path, video_uri, interval))
        while True:
            for c in camera_dumps:
                c.dump_frame()
    else:
        log.error("No config file provided! Exiting app...")