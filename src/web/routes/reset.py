import time
from fastapi import APIRouter, Response, status

from src.web.models.controller import ControllerIds
from src.web.models.drinker import Drinker

from src.controller.controller_api import controller_api
from src.controller.serial_api import reset_serial

reset_router = APIRouter()

@reset_router.post("/serial")
async def reset_serial_controller_endpoint():
    # we open serial port and it resets controller
    try:
        # get feeder params
        feeder_params = {}
        controller_ids = controller_api.feeder_get_controller_ids()
        for controller_id in controller_ids:
            [feeder_box_open_angle,
             feeder_box_close_angle] = controller_api.feeder_box_get_servo_open_close_angles(
                controller_id=controller_id)
            [feeder_gate_open_angle,
             feeder_gate_close_angle] = controller_api.feeder_gate_get_servo_open_close_angles(
                controller_id=controller_id)
            feeder_params[controller_id] = {
                "feeder_box_open_angle": feeder_box_open_angle,
                "feeder_box_close_angle": feeder_box_close_angle,
                "feeder_gate_open_angle": feeder_gate_open_angle,
                "feeder_gate_close_angle": feeder_gate_close_angle
            }
        # get drinker params
        drinker_params = {}
        controller_ids = controller_api.drinker_get_controller_ids()
        for controller_id in controller_ids:
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

            drinker_params[controller_id] = {
                "drinker_input_open_angle": drinker_input_open_angle,
                "drinker_input_close_angle": drinker_input_close_angle,
                "drinker_output_open_angle": drinker_output_open_angle,
                "drinker_output_close_angle": drinker_output_close_angle,
                "water_level_measure_iterations": water_level_measure_iterations,
                "water_level_max_cm_distance": water_level_max_cm_distance,
                "water_level_max_level": water_level_max_level,
                "water_level_min_level": water_level_min_level
            }

        print(feeder_params)
        print(drinker_params)
        # reset_status = reset_serial()
        reset_status = True
        if reset_status:
            # set feeder params
            for controller_id, params in feeder_params.items():
                controller_api.feeder_box_set_servo_open_close_angles(
                    controller_id=controller_id,
                    feeder_box_open_angle=params["feeder_box_open_angle"],
                    feeder_box_close_angle=params["feeder_box_close_angle"])
                controller_api.feeder_gate_set_servo_open_close_angles(
                    controller_id=controller_id,
                    feeder_gate_open_angle=params["feeder_gate_open_angle"],
                    feeder_gate_close_angle=params["feeder_gate_close_angle"])
            # set drinker params
            for controller_id, params in drinker_params.items():
                controller_api.drinker_input_set_servo_open_close_angles(
                    controller_id=controller_id,
                    drinker_input_open_angle=params["drinker_input_open_angle"],
                    drinker_input_close_angle=params["drinker_input_close_angle"])
                controller_api.drinker_output_set_servo_open_close_angles(
                    controller_id=controller_id,
                    drinker_output_open_angle=params["drinker_output_open_angle"],
                    drinker_output_close_angle=params["drinker_output_close_angle"])
                controller_api.drinker_water_level_set_params(
                    controller_id=controller_id,
                    water_level_measure_iterations=params["water_level_measure_iterations"],
                    water_level_max_cm_distance=params["water_level_max_cm_distance"],
                    water_level_max_level=params["water_level_max_level"],
                    water_level_min_level=params["water_level_min_level"])

            return Response(status_code=status.HTTP_200_OK)
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
# @reset_router.post("/spi")
# async def reset_spi_controller_endpoint():
#     # we send order 66 command to controller and it does software reset
#     try:
#         # get feeder params
#         feeder_params = {}
#         controller_ids = controller_api.feeder_get_controller_ids()
#         for controller_id in controller_ids:
#             [feeder_box_open_angle,
#              feeder_box_close_angle] = controller_api.feeder_box_get_servo_open_close_angles(
#                 controller_id=controller_id)
#             [feeder_gate_open_angle,
#              feeder_gate_close_angle] = controller_api.feeder_gate_get_servo_open_close_angles(
#                 controller_id=controller_id)
#             feeder_params[controller_id] = {
#                 "feeder_box_open_angle": feeder_box_open_angle,
#                 "feeder_box_close_angle": feeder_box_close_angle,
#                 "feeder_gate_open_angle": feeder_gate_open_angle,
#                 "feeder_gate_close_angle": feeder_gate_close_angle
#             }
#         # get drinker params
#         drinker_params = {}
#         controller_ids = controller_api.drinker_get_controller_ids()
#         for controller_id in controller_ids:
#             [
#                 drinker_input_open_angle,
#                 drinker_input_close_angle
#             ] = controller_api.drinker_input_get_servo_open_close_angles(
#                 controller_id=controller_id)
#             [
#                 drinker_output_open_angle,
#                 drinker_output_close_angle
#             ] = controller_api.drinker_output_get_servo_open_close_angles(
#                 controller_id=controller_id)
#             [
#                 water_level_measure_iterations,
#                 water_level_max_cm_distance,
#                 water_level_max_level,
#                 water_level_min_level
#             ] = controller_api.drinker_water_level_get_params(
#                 controller_id=controller_id)
#
#             drinker_params[controller_id] = {
#                 "drinker_input_open_angle": drinker_input_open_angle,
#                 "drinker_input_close_angle": drinker_input_close_angle,
#                 "drinker_output_open_angle": drinker_output_open_angle,
#                 "drinker_output_close_angle": drinker_output_close_angle,
#                 "water_level_measure_iterations": water_level_measure_iterations,
#                 "water_level_max_cm_distance": water_level_max_cm_distance,
#                 "water_level_max_level": water_level_max_level,
#                 "water_level_min_level": water_level_min_level
#             }
#         # reset controller
#         controller_api.controller_reset()
#
#         print(feeder_params)
#         print(drinker_params)
#         #
#         # # set feeder params
#         # for controller_id, params in feeder_params.items():
#         #     controller_api.feeder_box_set_servo_open_close_angles(
#         #         controller_id=controller_id,
#         #         feeder_box_open_angle=params["feeder_box_open_angle"],
#         #         feeder_box_close_angle=params["feeder_box_close_angle"])
#         #     controller_api.feeder_gate_set_servo_open_close_angles(
#         #         controller_id=controller_id,
#         #         feeder_gate_open_angle=params["feeder_gate_open_angle"],
#         #         feeder_gate_close_angle=params["feeder_gate_close_angle"])
#         # # set drinker params
#         # for controller_id, params in drinker_params.items():
#         #     controller_api.drinker_input_set_servo_open_close_angles(
#         #         controller_id=controller_id,
#         #         drinker_input_open_angle=params["drinker_input_open_angle"],
#         #         drinker_input_close_angle=params["drinker_input_close_angle"])
#         #     controller_api.drinker_output_set_servo_open_close_angles(
#         #         controller_id=controller_id,
#         #         drinker_output_open_angle=params["drinker_output_open_angle"],
#         #         drinker_output_close_angle=params["drinker_output_close_angle"])
#         #     controller_api.drinker_water_level_set_params(
#         #         controller_id=controller_id,
#         #         water_level_measure_iterations=params["water_level_measure_iterations"],
#         #         water_level_max_cm_distance=params["water_level_max_cm_distance"],
#         #         water_level_max_level=params["water_level_max_level"],
#         #         water_level_min_level=params["water_level_min_level"])
#
#         return Response(status_code=status.HTTP_200_OK)
#     except AssertionError as e:
#         print(e)
#         return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
