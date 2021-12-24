from fastapi import APIRouter, Response, status

from src.web.models.controller import ControllerIds
from src.web.models.drinker import Drinker

from src.controller.controller_api import controller_api

drinker_router = APIRouter()


@drinker_router.get("/")
async def get_drinker_controllers_endpoint():
    controller_ids = controller_api.drinker_get_controller_ids()
    return ControllerIds(
        controller_ids=controller_ids
    )


@drinker_router.get("/{controller_id}", response_model=Drinker)
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

@drinker_router.get("/{controller_id}/params", response_model=Drinker)
async def drinker_params_endpoint(controller_id: int):
    [
        drinker_input_angle,
        drinker_output_angle,
        drinker_water_level_current,
        drinker_empty_flag,
        drinker_fill_flag
    ] = controller_api.drinker_get_params(
        controller_id=controller_id)

    return Drinker(
        drinker_input_angle=drinker_input_angle,
        drinker_output_angle=drinker_output_angle,
        drinker_water_level_current=drinker_water_level_current,
        drinker_empty_flag=drinker_empty_flag,
        drinker_fill_flag=drinker_fill_flag
    )


@drinker_router.get("/{controller_id}/output_open_close_angles", response_model=Drinker)
async def drinker_output_get_open_close_angles_endpoint(controller_id: int):

    [
        drinker_output_open_angle,
        drinker_output_close_angle
    ] = controller_api.drinker_output_get_servo_open_close_angles(
        controller_id=controller_id)

    return Drinker(
        drinker_output_open_angle=drinker_output_open_angle,
        drinker_output_close_angle=drinker_output_close_angle)


@drinker_router.get("/{controller_id}/input_open_close_angles", response_model=Drinker)
async def drinker_input_get_open_close_angles_endpoint(controller_id: int):
    [
        drinker_input_open_angle,
        drinker_input_close_angle
    ] = controller_api.drinker_input_get_servo_open_close_angles(
        controller_id=controller_id)

    return Drinker(
        drinker_input_open_angle=drinker_input_open_angle,
        drinker_input_close_angle=drinker_input_close_angle)

@drinker_router.post("/{controller_id}/input_open_close_angles")
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


@drinker_router.post("/{controller_id}/output_set_open_close_angles")
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


@drinker_router.get("/{controller_id}/water_level_params", response_model=Drinker)
async def get_drinker_water_level_get_params_endpoint(controller_id: int):
    try:
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
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@drinker_router.post("/{controller_id}/water_level_params")
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

@drinker_router.get("/{controller_id}/water_level_moving_average")
async def drinker_water_level_moving_average_endpoint(controller_id: int):
    try:
        drinker_water_level_moving_average = controller_api.drinker_water_level_get_moving_average(controller_id=controller_id)
        return Drinker(drinker_water_level_moving_average=drinker_water_level_moving_average, skip_defaults=True, exclude_unset=True)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@drinker_router.post("/{controller_id}/input_open")
async def drinker_input_open_endpoint(controller_id: int):
    try:
        controller_api.drinker_input_open(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@drinker_router.post("/{controller_id}/input_close")
async def drinker_input_close_endpoint(controller_id: int):
    try:
        controller_api.drinker_input_close(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@drinker_router.post("/{controller_id}/input_set_angle")
async def drinker_input_set_angle_endpoint(controller_id: int, angle: int):
    try:
        controller_api.drinker_input_set_angle(controller_id=controller_id, angle=angle)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@drinker_router.post("/{controller_id}/output_open")
async def drinker_output_open_endpoint(controller_id: int):
    try:
        controller_api.drinker_output_open(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@drinker_router.post("/{controller_id}/output_close")
async def drinker_output_close_endpoint(controller_id: int):
    try:
        controller_api.drinker_output_close(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@drinker_router.post("/{controller_id}/output_set_angle")
async def drinker_output_set_angle_endpoint(controller_id: int, angle: int):
    try:
        controller_api.drinker_output_set_angle(controller_id=controller_id, angle=angle)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@drinker_router.post("/{controller_id}/fill")
async def drinker_fill_endpoint(controller_id: int):
    try:
        controller_api.drinker_fill(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@drinker_router.post("/{controller_id}/empty")
async def drinker_empty_endpoint(controller_id: int):
    try:
        controller_api.drinker_empty(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@drinker_router.post("/{controller_id}/reset")
async def drinker_drinker_reset_endpoint(controller_id: int):
    try:
        controller_api.drinker_reset(controller_id=controller_id)
        return Response(status_code=status.HTTP_200_OK)
    except AssertionError as e:
        print(e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

