from __future__ import annotations
import logging
import cv2
import numpy as np
from timeout_decorator import timeout_decorator
from src.camera.common import ReadFrameException


logger = logging.getLogger(name=__name__)

FRAME_READ_TIMEOUT = 1


class Camera:

    def __init__(self, source: str | int = None):
        self.source = source
        self.cap = None
        self.initialize()

    def initialize(self) -> None:
        if self.cap is None:
            logger.info(f"{self.source}: init VideoCapture")
            self.cap = cv2.VideoCapture(self.source)

    def deinitialize(self) -> None:
        if self.cap is not None:
            self.cap.release()
        self.cap = None

    @timeout_decorator.timeout(FRAME_READ_TIMEOUT, use_signals=False)
    def read(self) -> np.ndarray:
        if self.cap is None:
            raise ReadFrameException("Not initialized")
        ret, image = self.cap.read()
        if ret:
            return image
        else:
            raise ReadFrameException("Empty frame")

    def set_resolution(self, width, height) -> None:
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_resolution(self) -> list[int]:
        current_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        current_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return [current_width, current_height]

    def get_max_resolution(self) -> list[int]:
        """
        https://stackoverflow.com/questions/18458422/query-maximum-webcam-resolution-in-opencv
        """
        high_value = 10000
        current_width, current_height = self.get_resolution()
        self.set_resolution(high_value, high_value)

        max_width, max_height = self.get_resolution()
        self.set_resolution(current_width, current_height)
        return [max_width, max_height]
