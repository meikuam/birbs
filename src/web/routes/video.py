from typing import Optional, Dict, List
from fastapi import APIRouter, Request, Response, status, Depends
from fastapi.responses import StreamingResponse
import asyncio

from src.camera.camera import camera_streams_container
from src.web.database.user_manager import current_superuser
from src.web.database.users import User

video_router = APIRouter()


@video_router.on_event("shutdown")
async def shutdown_event():
    camera_streams_container.stop_streams()


@video_router.get("/")
def video_devices_endpoint(user: User = Depends(current_superuser)):
    return {"devices": camera_streams_container.get_device_ids()}


@video_router.get("/{device_id}")
def video_endpoint(device_id: int, response: Response, user: User = Depends(current_superuser)):
    if device_id not in camera_streams_container.get_device_ids():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return None
    else:
        print("select stream")
        camera_streams_container.select_stream(device_id=device_id)
        print("make stream responce")
        print(camera_streams_container.get_frame(encode=True))
        return StreamingResponse(
            camera_streams_container.get_frame(encode=True),
            media_type='multipart/x-mixed-replace; boundary=frame')
