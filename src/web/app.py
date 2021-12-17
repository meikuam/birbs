import os
import sys
sys.path.append('.')

import uvicorn
from typing import Optional, Dict, List
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse, UJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.controller.controller_api import ControllerApi
from src.camera.camera import CameraStream, get_available_camera_streams

class Leds(BaseModel):
    state: Optional[bool]
    value: Optional[int]


class ControllerIds(BaseModel):
    controller_ids: List[int]


class Feeder(BaseModel):
    feeder_box_angle: Optional[int]
    feeder_gate_angle: Optional[int]
    feeder_box_open_angle: Optional[int]
    feeder_box_close_angle: Optional[int]
    feeder_gate_open_angle: Optional[int]
    feeder_gate_close_angle: Optional[int]


class Drinker(BaseModel):
    drinker_input_angle: Optional[int]
    drinker_output_angle: Optional[int]
    drinker_water_level_current: Optional[int]
    drinker_empty_flag: Optional[bool]
    drinker_fill_flag: Optional[bool]
    drinker_input_open_angle: Optional[int]
    drinker_input_close_angle: Optional[int]
    drinker_output_open_angle: Optional[int]
    drinker_output_close_angle: Optional[int]
    water_level_measure_iterations: Optional[int]
    water_level_max_cm_distance: Optional[int]
    water_level_max_level: Optional[int]
    water_level_min_level: Optional[int]


controller_api: ControllerApi = ControllerApi()
camera_stream: Dict[int, CameraStream] = get_available_camera_streams()

for key, item in camera_stream.items():
    item.start()

app = FastAPI()

app.mount("/static", StaticFiles(directory="www/static"), name="static")
templates = Jinja2Templates(directory="www/templates")


# @app.on_event("startup")
# async def startup_event():
#     controller_api = ControllerApi()

@app.get("/")
def index( request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/leds", response_model=Leds)
async def get_leds_state_endpoint():
    state, value = controller_api.leds_get()
    return Leds(
        state=state,
        value=value
    )


@app.post("/api/leds")
async def set_leds_state_endpoint(leds: Leds, response: Response):
    if leds.state is not None:
        controller_api.leds_status_set(leds.state)
    if leds.value is not None:
        controller_api.leds_value_set(leds.value)
    return Response(status_code=status.HTTP_200_OK)

@app.get("/api/feeder")
async def get_feeder_state_endpoint():
    controller_ids = controller_api.feeder_get_controller_ids()
    return ControllerIds(
        controller_ids=controller_ids
    )


@app.get("/api/feeder/{controller_id}", response_model=Feeder)
async def get_feeder_state_endpoint(controller_id: int):
    [feeder_box_angle,
     feeder_gate_angle] = controller_api.feeder_get_servo_angle(
        controller_id=controller_id)
    [feeder_box_open_angle,
     feeder_box_close_angle] = controller_api.feeder_box_get_servo_open_close_angles(
        controller_id=controller_id)
    [feeder_gate_open_angle,
     feeder_gate_close_angle] = controller_api.feeder_gate_get_servo_open_close_angles(
        controller_id=controller_id)
    return Feeder(
        feeder_box_angle=feeder_box_angle,
        feeder_gate_angle=feeder_gate_angle,
        feeder_box_open_angle=feeder_box_open_angle,
        feeder_box_close_angle=feeder_box_close_angle,
        feeder_gate_open_angle=feeder_gate_open_angle,
        feeder_gate_close_angle=feeder_gate_close_angle)

@app.post("/api/feeder/{controller_id}/gate_set_open_close_angles")
async def feeder_gate_set_open_close_angles_endpoint(controller_id: int, open_angle: int, close_angle: int):
    try:
        controller_api.feeder_gate_set_servo_open_close_angles(
            controller_id=controller_id,
            feeder_gate_open_angle=open_angle,
            feeder_gate_close_angle=close_angle)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/api/feeder/{controller_id}/box_set_open_close_angles")
async def feeder_box_set_open_close_angles_endpoint(controller_id: int, open_angle: int, close_angle: int):
    try:
        controller_api.feeder_box_set_servo_open_close_angles(
            controller_id=controller_id,
            feeder_box_open_angle=open_angle,
            feeder_box_close_angle=close_angle)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/api/feeder/{controller_id}/box_open")
async def feeder_box_open_endpoint(controller_id: int):
    try:
        controller_api.feeder_box_open(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/feeder/{controller_id}/box_close")
async def feeder_box_close_endpoint(controller_id: int):
    try:
        controller_api.feeder_box_close(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/feeder/{controller_id}/box_set_angle")
async def feeder_box_set_angle_endpoint(controller_id: int, angle: int):
    try:
        controller_api.feeder_box_set_angle(controller_id=controller_id, angle=angle)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/feeder/{controller_id}/gate_open")
async def feeder_gate_open_endpoint(controller_id: int):
    try:
        controller_api.feeder_gate_open(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/feeder/{controller_id}/gate_close")
async def feeder_gate_close_endpoint(controller_id: int):
    try:
        controller_api.feeder_gate_close(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/feeder/{controller_id}/gate_set_angle")
async def feeder_gate_set_angle_endpoint(controller_id: int, angle: int):
    try:
        controller_api.feeder_gate_set_angle(controller_id=controller_id, angle=angle)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/feeder/{controller_id}/gate_feed")
async def feeder_gate_feed_endpoint(controller_id: int):
    try:
        controller_api.feeder_gate_feed(
            controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/feeder/{controller_id}/gate_feed_ms")
async def feeder_gate_feed_endpoint(controller_id: int, delay_ms: int = 100):
    try:
        controller_api.feeder_gate_feed_ms(
            controller_id=controller_id,
            ms=delay_ms)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/api/drinker/{controller_id}", response_model=Drinker)
async def get_drinker_state_endpoint(controller_id: int):
    [
        drinker_input_angle,
        drinker_output_angle,
        drinker_water_level_current,
        drinker_empty_flag,
        drinker_fill_flag
    ] = controller_api.drinker_get_params(
        controller_id=controller_id)

    [
        drinker_input_open_angle,
        drinker_input_close_angle
    ] = controller_api.drinker_input_get_servo_open_close_angles(
        controller_id=controller_id)
    [
        drinker_output_open_angle,
        drinker_output_close_angle
    ] = controller_api.drinker_output_get_servo_open_close_angles(
        controller_id=controller_id)

    [
        water_level_measure_iterations,
        water_level_max_cm_distance,
        water_level_max_level,
        water_level_min_level
    ] = controller_api.drinker_water_level_get_params(
        controller_id=controller_id)
    return Drinker(
        drinker_input_angle=drinker_input_angle,
        drinker_input_open_angle=drinker_input_open_angle,
        drinker_input_close_angle=drinker_input_close_angle,
        drinker_output_angle=drinker_output_angle,
        drinker_output_open_angle=drinker_output_open_angle,
        drinker_output_close_angle=drinker_output_close_angle,
        drinker_water_level_current=drinker_water_level_current,
        drinker_empty_flag=drinker_empty_flag,
        drinker_fill_flag=drinker_fill_flag,
        water_level_measure_iterations=water_level_measure_iterations,
        water_level_max_cm_distance=water_level_max_cm_distance,
        water_level_max_level=water_level_max_level,
        water_level_min_level=water_level_min_level
    )

@app.get("/api/drinker/{controller_id}/output_open_close_angles", response_model=Drinker)
async def get_drinker_state_endpoint(controller_id: int):

    [
        drinker_output_open_angle,
        drinker_output_close_angle
    ] = controller_api.drinker_output_get_servo_open_close_angles(
        controller_id=controller_id)

    return Drinker(
        drinker_output_open_angle=drinker_output_open_angle,
        drinker_output_close_angle=drinker_output_close_angle)


@app.get("/api/drinker/{controller_id}/input_open_close_angles", response_model=Drinker)
async def get_drinker_state_endpoint(controller_id: int):
    [
        drinker_input_open_angle,
        drinker_input_close_angle
    ] = controller_api.drinker_input_get_servo_open_close_angles(
        controller_id=controller_id)

    return Drinker(
        drinker_input_open_angle=drinker_input_open_angle,
        drinker_input_close_angle=drinker_input_close_angle)

@app.get("/api/drinker/{controller_id}/water_level_params", response_model=Drinker)
async def get_drinker_state_endpoint(controller_id: int):
    [
        water_level_measure_iterations,
        water_level_max_cm_distance,
        water_level_max_level,
        water_level_min_level
    ] = controller_api.drinker_water_level_get_params(
        controller_id=controller_id)
    return Drinker(
        water_level_measure_iterations=water_level_measure_iterations,
        water_level_max_cm_distance=water_level_max_cm_distance,
        water_level_max_level=water_level_max_level,
        water_level_min_level=water_level_min_level)

@app.post("/api/drinker/{controller_id}/input_set_open_close_angles")
async def drinker_input_set_open_close_angles_endpoint(controller_id: int, open_angle: int, close_angle: int):
    try:
        controller_api.drinker_input_set_servo_open_close_angles(
            controller_id=controller_id,
            drinker_input_open_angle=open_angle,
            drinker_input_close_angle=close_angle)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/api/drinker/{controller_id}/output_set_open_close_angles")
async def drinker_output_set_open_close_angles_endpoint(controller_id: int, open_angle: int, close_angle: int):
    try:
        controller_api.drinker_output_set_servo_open_close_angles(
            controller_id=controller_id,
            drinker_output_open_angle=open_angle,
            drinker_output_close_angle=close_angle)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/api/drinker/{controller_id}/water_level_params")
async def drinker_water_level_set_params_endpoint(controller_id: int, measure_iterations: int, max_cm_distance: int, max_level: int, min_level: int):
    try:
        controller_api.drinker_water_level_set_params(
            controller_id=controller_id,
            water_level_measure_iterations=measure_iterations,
            water_level_max_cm_distance=max_cm_distance,
            water_level_max_level=max_level,
            water_level_min_level=min_level)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/drinker/{controller_id}/water_level_current")
async def drinker_input_open_endpoint(controller_id: int):
    try:
        drinker_water_level_current = controller_api.drinker_water_level_get_current(controller_id=controller_id)
        return Drinker(drinker_water_level_current=drinker_water_level_current)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/api/drinker/{controller_id}/input_open")
async def drinker_input_open_endpoint(controller_id: int):
    try:
        controller_api.drinker_input_open(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/drinker/{controller_id}/input_close")
async def drinker_input_close_endpoint(controller_id: int):
    try:
        controller_api.drinker_input_close(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/drinker/{controller_id}/input_set_angle")
async def drinker_input_set_angle_endpoint(controller_id: int, angle: int):
    try:
        controller_api.drinker_input_set_angle(controller_id=controller_id, angle=angle)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/drinker/{controller_id}/output_open")
async def drinker_output_open_endpoint(controller_id: int):
    try:
        controller_api.drinker_output_open(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/drinker/{controller_id}/output_close")
async def drinker_output_close_endpoint(controller_id: int):
    try:
        controller_api.drinker_output_close(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/drinker/{controller_id}/output_set_angle")
async def drinker_output_set_angle_endpoint(controller_id: int, angle: int):
    try:
        controller_api.drinker_output_set_angle(controller_id=controller_id, angle=angle)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/drinker/{controller_id}/fill")
async def drinker_fill_endpoint(controller_id: int):
    try:
        controller_api.drinker_fill(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/drinker/{controller_id}/empty")
async def drinker_empty_endpoint(controller_id: int):
    try:
        controller_api.drinker_empty(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/api/drinker/{controller_id}/reset")
async def drinker_drinker_reset_endpoint(controller_id: int):
    try:
        controller_api.drinker_reset(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/video")
async def index(request: Request):
    return templates.TemplateResponse("video.html", {"request": request})

@app.get("/api/video")
def video_devices_endpoint():
    return {"devices": list(camera_stream.keys())}

@app.get("/api/video/{device_id}")
def video_endpoint(device_id: int, response: Response):
    if device_id not in camera_stream.keys():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return None
    else:
        return StreamingResponse(camera_stream[device_id].get_frame(), media_type='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info")
