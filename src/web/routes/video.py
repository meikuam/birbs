from fastapi import APIRouter, Response, status
from fastapi.responses import StreamingResponse
import logging

from src.camera.container import CameraStreamsContianer

logger = logging.getLogger(name=__name__)

container = CameraStreamsContianer()
video_router = APIRouter()


@video_router.on_event("shutdown")
async def shutdown_event():
    container.stop_streams()


@video_router.get("/")
def video_devices_endpoint():
    return {"devices": container.device_ids()}


@video_router.get("/{device_id}")
def video_endpoint(device_id: int, response: Response):
    if device_id not in container.device_ids():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return None
    else:
        logger.info("select stream")
        container.select_stream(device_id=device_id)
        logger.info(f"make stream responce with device_id: {device_id}")
        return StreamingResponse(
            container.stream_frame(encode=True),
            media_type='multipart/x-mixed-replace; boundary=frame')
