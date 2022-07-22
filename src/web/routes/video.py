from typing import Optional, Dict, List
from fastapi import APIRouter, Request, Response, status, Depends
from fastapi.responses import StreamingResponse
from fastapi import WebSocket
import asyncio

from src.camera.camera import CameraStream, get_available_camera_streams
from src.web.database.user_manager import current_superuser
from src.web.database.users import User

video_router = APIRouter()


camera_stream: Dict[int, CameraStream] = get_available_camera_streams()
# camera_stream = {
#     1: CameraStream(1, True)
# }
#
# for key, item in camera_stream.items():
#     item.start()


@video_router.on_event("shutdown")
async def startup_event():
    for id, cam_stream in camera_stream.items():
        cam_stream.stop()


@video_router.get("/")
def video_devices_endpoint(user: User = Depends(current_superuser)):
    return {"devices": list(camera_stream.keys())}


@video_router.get("/{device_id}")
def video_endpoint(device_id: int, response: Response, user: User = Depends(current_superuser)):
    if device_id not in camera_stream.keys():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return None
    else:
        for id, cam_stream in camera_stream.items():
            if id == device_id:
                continue
            cam_stream.stop()
        camera_stream[device_id].start()
        return StreamingResponse(
            camera_stream[device_id].get_frame(),
            media_type='multipart/x-mixed-replace; boundary=frame')
