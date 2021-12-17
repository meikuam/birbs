import os
import cv2
import time
from datetime import datetime
import numpy as np
from typing import List
from threading import Thread, Lock


def image_put_text(image: np.ndarray, text: str, bottom_left_point: List[int]) -> np.ndarray:
    image = cv2.putText(
        img=image,
        text=text,
        org=bottom_left_point,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1,
        color=(255, 255, 255),
        thickness=2
    )
    return image


class CameraStream:
    def __init__(self, src=None, add_date=False):
        self.cap = cv2.VideoCapture(src, cv2.CAP_V4L2)
        self.add_date = add_date
        self.thread = None
        self.stream_running = False
        self.output = np.zeros([1, 1, 3])
        self.lock = Lock()
        self.set_resolution(320, 240)
        self.set_resolution(256, 192)

    def set_resolution(self, width, height):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_resolution(self) -> List[int]:
        current_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        current_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return [current_width, current_height]

    def get_max_resolution(self) -> List[int]:
        """
        https://stackoverflow.com/questions/18458422/query-maximum-webcam-resolution-in-opencv
        """
        high_value = 10000
        current_width, current_height = self.get_resolution()
        self.set_resolution(high_value, high_value)

        max_width, max_height = self.get_resolution()
        self.set_resolution(current_width, current_height)
        return [max_width, max_height]

    """
    resolutions = {}

for index, row in table[["W", "H"]].iterrows():
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, row["W"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, row["H"])
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    resolutions[str(width)+"x"+str(height)] = "OK"
    """

    def get_frame(self):
        while True:
            with self.lock:
                if self.output is None:
                    continue
                flag, image = cv2.imencode('.jpg', self.output)
                if not flag:
                    continue
                yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(image) + b'\r\n'

    def stream_function(self):
        while self.stream_running:
            ret_val, img = self.cap.read()
            if self.add_date:
                img = image_put_text(img, datetime.now().strftime("%d.%m.%Y %H:%M:%S"), [50, 50])
            if ret_val:
                with self.lock:
                    self.output = img
            else:
                print("error get frame")
                time.sleep(1)

    def start(self):
        print("start thread")
        self.stream_running = True
        self.thread = Thread(target=self.stream_function, args=())
        self.thread.start()
        print("thread started")

    def stop(self):
        if self.thread is not None:
            print("stop thread")
            self.stream_running = False
            self.thread.join()
            print("thread stopped")


def get_available_camera_streams(key_index=True):
    devices = [os.path.join("/dev", device) for device in os.listdir("/dev") if "video" in device]

    camera_streams = {}
    for device in devices:
        camera_stream = CameraStream(src=device)
        if camera_stream.get_resolution()[0] > 0:
            print("add device", device, camera_stream.get_resolution())
            if key_index:  #TODO: use index instead of path
                device_id = int(device[len("/dev/video"):])
                camera_streams[device_id] = camera_stream
            else:
                camera_streams[device] = camera_stream

    return camera_streams
