from __future__ import annotations
import os
import logging


import cv2
import time
from datetime import datetime
import numpy as np
from src.time.time import local_now
from src.camera.camera import Camera
from src.camera.camera_stream import CameraStream


logger = logging.getLogger(name=__name__)


def get_available_camera_streams(key_index=True) -> dict[str, CameraStream]:
    devices = [
        os.path.join("/dev", device)
        for device in os.listdir("/dev")
        if "video" in device
    ]

    camera_streams = {}
    for device in devices:
        camera = Camera(source=device)
        resolution = camera.get_resolution()
        if resolution[0] > 0:
            logging.info(f"add device {device}, {resolution}")
            camera.deinitialize()
            camera_stream = CameraStream(camera, print_date=True)
            if key_index:
                device_id = int(device[len("/dev/video"):])
                camera_streams[device_id] = camera_stream
            else:
                camera_streams[device] = camera_stream

    return camera_streams


class CameraStreamsContianer:

    def __init__(self):
        self.current_device_id = None
        self.camera_streams = get_available_camera_streams(key_index=True)

    def device_ids(self):
        return list(self.camera_streams.keys())

    def stop_streams(self):
        for idx, camera_stream in self.camera_streams.items():
            camera_stream.stop()

    def select_stream(self, device_id: int):
        if device_id not in self.device_ids():
            return False
        for idx, cam_stream in self.camera_streams.items():
            if idx != device_id:
                cam_stream.stop()
        logging.info(f"select_stream device {device_id}")
        self.device_id = device_id
        self.camera_streams[self.device_id].start()
        return True

    def get_frame(self, encode=True):
        if self.device_id is None:
            return None
        return self.camera_streams[self.device_id].get_frame(encode=encode)

    def stream_frame(self, encode=True):
        if self.device_id is None:
            return None
        return self.camera_streams[self.device_id].stream_frame(encode=encode)
