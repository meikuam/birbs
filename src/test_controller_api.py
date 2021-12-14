import sys
sys.path.append(".")
import time
from src.controller.controller_api import ControllerApi


if __name__ == "__main__":
    controller_api = ControllerApi()

    while True:
        led_state, led_value = controller_api.leds_get()
        print(f"led_state: {led_state} led_value: {led_value}")

        print("feeder [1]: ")
        [feeder_box_angle, feeder_gate_angle] = controller_api.feeder_get_servo_angle(1)
        print(f"\t feeder_box_angle: {feeder_box_angle} feeder_gate_angle: {feeder_gate_angle}")

        print("feeder [2]: ")
        [feeder_box_angle, feeder_gate_angle] = controller_api.feeder_get_servo_angle(2)
        print(f"\t feeder_box_angle: {feeder_box_angle} feeder_gate_angle: {feeder_gate_angle}")


        print("drinker [1]: ")
        [
            drinker_input_angle,
            drinker_output_angle,
            drinker_water_level_current,
            drinker_empty_flag,
            drinker_fill_flag
        ] = controller_api.drinker_get_params(1)
        print(f"\tdrinker_input_angle: {drinker_input_angle} drinker_output_angle: {drinker_output_angle} drinker_water_level_current: {drinker_water_level_current} drinker_empty_flag: {drinker_empty_flag}, drinker_fill_flag: {drinker_fill_flag}")
        [
            water_level_measure_iterations,
            water_level_max_cm_distance,
            water_level_max_level,
            water_level_min_level
        ] = controller_api.drinker_water_level_get_params(1)
        print(f"\t water_level_measure_iterations: {water_level_measure_iterations}, water_level_max_cm_distance: {water_level_max_cm_distance} water_level_max_level: {water_level_max_level} water_level_min_level: {water_level_min_level}")

        print("drinker [2]: ")
        [
            drinker_input_angle,
            drinker_output_angle,
            drinker_water_level_current,
            drinker_empty_flag,
            drinker_fill_flag
        ] = controller_api.drinker_get_params(2)
        print(f"\tdrinker_input_angle: {drinker_input_angle} drinker_output_angle: {drinker_output_angle} drinker_water_level_current: {drinker_water_level_current} drinker_empty_flag: {drinker_empty_flag}, drinker_fill_flag: {drinker_fill_flag}")
        [
            water_level_measure_iterations,
            water_level_max_cm_distance,
            water_level_max_level,
            water_level_min_level
        ] = controller_api.drinker_water_level_get_params(1)
        print(f"\t water_level_measure_iterations: {water_level_measure_iterations}, water_level_max_cm_distance: {water_level_max_cm_distance} water_level_max_level: {water_level_max_level} water_level_min_level: {water_level_min_level}")
        time.sleep(0.01)
