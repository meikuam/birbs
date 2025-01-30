from __future__ import annotations
from typing import Literal
import cv2
from src.camera.container import CameraStreamsContianer
from src.telegram.bot import log_image, log_message


class CameraTelegramLogging:

    def __init__(self, camera_container: CameraStreamsContianer):
        self.camera_container = camera_container
        self.device_mapping = {
            "pop": {
                "feeder": 0,
                "drinker": 6
            },
            "pek": {
                "feeder": 4,
                "drinker": 2
            }
        }

    def get_frame_from_stream(
        self,
        birb_id: Literal["pek", "pop"],
        device_type: Literal["feeder", "drinker"]
    ):
        device_id = self.device_mapping[birb_id][device_type]
        stream_select_state = self.camera_container.select_stream(device_id)
        if stream_select_state:
            return next(self.camera_container.stream_frame(encode=False))
        else:
            return None

    async def log_stream_frame(
        self,
        birb_id: Literal["pek", "pop"],
        device_type: Literal["feeder", "drinker"],
        alt_text: str = None
    ):
        frame = self.get_frame_from_stream(birb_id=birb_id, device_type=device_type)
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            await log_image(frame, caption=alt_text)
        else:
            if alt_text:
                await log_message(message=f"{birb_id}, {device_type}: {alt_text}")

    async def log_message(self, text: str = None):
        await log_message(text)
