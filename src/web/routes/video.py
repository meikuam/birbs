from typing import Optional, Dict, List
from fastapi import APIRouter, Request, Response, status
from fastapi.responses import StreamingResponse

from src.camera.camera import CameraStream, get_available_camera_streams


video_router = APIRouter()


camera_stream: Dict[int, CameraStream] = get_available_camera_streams()

#
# for key, item in camera_stream.items():
#     item.start()


@video_router.get("/")
def video_devices_endpoint():
    return {"devices": list(camera_stream.keys())}

@video_router.get("/{device_id}")
def video_endpoint(device_id: int, response: Response):
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
