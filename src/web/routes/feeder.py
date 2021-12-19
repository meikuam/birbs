from fastapi import APIRouter, Response, status

from src.web.models.controller import ControllerIds
from src.web.models.feeder import Feeder

from src.controller.controller_api import controller_api

feeder_router = APIRouter()



@feeder_router.get("/")
async def get_feeder_state_endpoint():
    controller_ids = controller_api.feeder_get_controller_ids()
    return ControllerIds(
        controller_ids=controller_ids
    )


@feeder_router.get("/{controller_id}/params", response_model=Feeder)
async def get_feeder_params_endpoint(controller_id: int):
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


@feeder_router.get("/{controller_id}/servo_angle", response_model=Feeder)
async def get_feeder_params_endpoint(controller_id: int):
    [feeder_box_angle,
     feeder_gate_angle] = controller_api.feeder_get_servo_angle(
        controller_id=controller_id)
    return Feeder(
        feeder_box_angle=feeder_box_angle,
        feeder_gate_angle=feeder_gate_angle)


@feeder_router.get("/{controller_id}/gate_open_close_angles", response_model=Feeder)
async def get_feeder_params_endpoint(controller_id: int):
    [feeder_gate_open_angle,
     feeder_gate_close_angle] = controller_api.feeder_gate_get_servo_open_close_angles(
        controller_id=controller_id)
    return Feeder(
        feeder_gate_open_angle=feeder_gate_open_angle,
        feeder_gate_close_angle=feeder_gate_close_angle)


@feeder_router.post("/{controller_id}/gate_open_close_angles")
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

@feeder_router.get("/{controller_id}/box_open_close_angles", response_model=Feeder)
async def get_feeder_params_endpoint(controller_id: int):
    [feeder_box_open_angle,
     feeder_box_close_angle] = controller_api.feeder_box_get_servo_open_close_angles(
        controller_id=controller_id)
    return Feeder(
        feeder_box_open_angle=feeder_box_open_angle,
        feeder_box_close_angle=feeder_box_close_angle)

@feeder_router.post("/{controller_id}/box_open_close_angles")
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


@feeder_router.post("/{controller_id}/box_open")
async def feeder_box_open_endpoint(controller_id: int):
    try:
        controller_api.feeder_box_open(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@feeder_router.post("/{controller_id}/box_close")
async def feeder_box_close_endpoint(controller_id: int):
    try:
        controller_api.feeder_box_close(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@feeder_router.post("/{controller_id}/box_set_angle")
async def feeder_box_set_angle_endpoint(controller_id: int, angle: int):
    try:
        controller_api.feeder_box_set_angle(controller_id=controller_id, angle=angle)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@feeder_router.post("/{controller_id}/gate_open")
async def feeder_gate_open_endpoint(controller_id: int):
    try:
        controller_api.feeder_gate_open(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@feeder_router.post("/{controller_id}/gate_close")
async def feeder_gate_close_endpoint(controller_id: int):
    try:
        controller_api.feeder_gate_close(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@feeder_router.post("/{controller_id}/gate_set_angle")
async def feeder_gate_set_angle_endpoint(controller_id: int, angle: int):
    try:
        controller_api.feeder_gate_set_angle(controller_id=controller_id, angle=angle)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@feeder_router.post("/{controller_id}/gate_feed")
async def feeder_gate_feed_endpoint(controller_id: int):
    try:
        controller_api.feeder_gate_feed(
            controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@feeder_router.post("/{controller_id}/gate_feed_ms")
async def feeder_gate_feed_ms_endpoint(controller_id: int, delay_ms: int = 100):
    try:
        controller_api.feeder_gate_feed_ms(
            controller_id=controller_id,
            ms=delay_ms)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
