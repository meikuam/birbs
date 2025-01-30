import cv2
import time
import logging
from threading import Thread
from timeout_decorator import timeout_decorator, TimeoutError

from src.time.time import local_now
from src.camera.common import image_put_text
from src.utils.common import TimeoutLock

logger = logging.getLogger(name=__name__)


FRAME_READ_TIMEOUT = 1


class ReadFrameException(Exception):
    pass


class CameraStream:
    def __init__(self, source=None, print_date=False, print_fps=False):
        self.print_date = print_date
        self.print_fps = print_fps
        self.source = source
        self.cap = None
        self.init_cap()
        self.thread = None
        self.stream_running = False
        self.current_frame = None
        self.lock = TimeoutLock()
        self.cooldown_timeout = 5
        self.lock_timeout = 1

    def init_cap(self) -> None:
        if self.cap is None:
            logger.info(f"{self.source}: init VideoCapture")
            self.cap = cv2.VideoCapture(self.source)

    def deinit_cap(self) -> None:
        self.current_frame = None
        if self.cap is not None:
            self.cap.release()
        self.cap = None

    def set_resolution(self, width, height) -> None:
        self.init_cap()
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_resolution(self) -> list[int]:
        self.init_cap()
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

    @timeout_decorator.timeout(FRAME_READ_TIMEOUT, use_signals=False)
    def read(self):
        ret, image = self.cap.read()
        if ret:
            return image
        else:
            raise ReadFrameException("Empty frame")

    def get_current_frame(self, encode=True):
        while True:
            with self.lock:
                if self.current_frame is None:
                    continue
                image = self.current_frame.copy()
            if encode:
                flag, image = cv2.imencode('.jpg', image)
                if not flag:
                    continue
                yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(image) + b'\r\n'
            else:
                yield image

    def _stream_function(self):
        while self.stream_running:
            try:
                start = time.perf_counter()
                image = self.read()
                elapsed = time.perf_counter() - start

                if self.print_date:
                    current_time = local_now().strftime("%d.%m.%Y %H:%M:%S")
                    current_time_position = [50, 50]
                    image = image_put_text(
                        image,
                        current_time,
                        current_time_position
                    )
                if self.print_fps:
                    fps = 1 / elapsed
                    current_fps = f"fps: {fps:.2f}"
                    current_fps_position = [50, 100]
                    image = image_put_text(
                        image,
                        current_fps,
                        current_fps_position
                    )

                with self.lock.acquire_timeout(self.lock_timeout) as acquire:
                    if acquire:
                        self.current_frame = image
                    else:
                        raise TimeoutError("Lock acquire timeout")

            except (TimeoutError, ReadFrameException) as e:
                logging.error(f"{self.source}: read error {e}")
                time.sleep(self.cooldown_seconds)

    def start(self):
        if not self.stream_running:
            logger.info(f"{self.source}: start thread")
            self.init_cap()
            self.stream_running = True
            self.thread = Thread(target=self._stream_function, args=())
            self.thread.start()
            logger.info(f"{self.source}: started thread")
        else:
            logger.info(f"{self.source}: already running thread")

    def stop(self):
        if self.thread is not None:
            logger.info(f"{self.source}: stop thread")
            self.stream_running = False
            self.thread.join()
            self.deinit_cap()
            logger.info(f"{self.source}: stopped thread")
        else:
            logger.info(f"{self.source}: already stopped thread")
