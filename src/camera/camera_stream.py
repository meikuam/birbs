import cv2
import time
import logging
from threading import Thread
from timeout_decorator import TimeoutError

from src.time.time import local_now
from src.camera.common import image_put_text, encode_image, ReadFrameException, EncodeImageException
from src.utils.common import TimeoutLock
from src.camera.camera import Camera

logger = logging.getLogger(name=__name__)


class CameraStream:
    def __init__(self, camera: Camera, print_date: bool = True, print_fps: bool = False):
        self.print_date = print_date
        self.print_fps = print_fps
        self.camera = camera
        self.current_frame = None
        self.lock = TimeoutLock()
        self.thread = None
        self.stream_running = False
        self.error_timeout = 5
        self.lock_timeout = 2

    def stream_frame(self, encode=True):
        while True:
            with self.lock.acquire_timeout(timeout=self.lock_timeout) as acquire:
                if not acquire or self.current_frame is None:
                    continue
                if self.stream_running is False:
                    raise ReadFrameException("Stream is not running")
                image = self.current_frame.copy()

            if encode:
                try:
                    yield encode_image(image)
                except EncodeImageException:
                    continue
            else:
                yield image

    def get_frame(self, encode=True):
        with self.lock.acquire_timeout(timeout=self.lock_timeout) as acquire:
            if not acquire or self.current_frame is None:
                raise ReadFrameException("Empty current stream frame")
            if self.stream_running is False:
                raise ReadFrameException("Stream is not running")
            image = self.current_frame.copy()

        if encode:
            return encode_image(image)
        else:
            return image

    def _stream_function(self):
        while self.stream_running:
            try:
                start = time.perf_counter()
                image = self.camera.read()
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
                logging.error(f"{self.camera.source}: read error {e}")
                self.camera.deinitialize()
                self.camera.initialize()
                time.sleep(self.error_timeout)

    def start(self):
        if not self.stream_running:
            logger.info(f"{self.camera.source}: start thread")
            self.camera.initialize()
            self.stream_running = True
            self.thread = Thread(target=self._stream_function, args=())
            self.thread.start()
            logger.info(f"{self.camera.source}: started thread")
        else:
            logger.info(f"{self.camera.source}: already running thread")

    def stop(self):
        if self.thread is not None:
            logger.info(f"{self.camera.source}: stop thread")
            self.stream_running = False
            self.current_frame = None
            self.thread.join()
            self.camera.deinitialize()
            logger.info(f"{self.camera.source}: stopped thread")
        else:
            logger.info(f"{self.camera.source}: already stopped thread")
