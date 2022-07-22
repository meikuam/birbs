from typing import List, Any
import periphery
from threading import Lock

import src.controller.commands as commands


def int2bytes(value: int) -> List[int]:
    return [(value & 0xFF00) >> 8, (value & 0xFF)]


def bytes2int(value: List[int]) -> int:
    return ((value[0] << 8) & 0xFF00) | (value[1] & 0xFF)


def set_byte_range(value: int) -> int:
    return max(min(value, 255), 0)

# metaclass singleton pattern
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ControllerApi(metaclass=Singleton):

    def __init__(self, devpath="/dev/spidev1.0", max_speed=3000):
        self.devpath = devpath
        self.max_speed = max_speed
        try:
            self.spi = periphery.SPI(
                devpath=self.devpath,
                mode=0,
                max_speed=self.max_speed,
                bit_order="msb",
                bits_per_word=8)
        except Exception as e:
            self.spi = None
            print(e)
        self.lock = Lock()

    def transfer(self, data_out: List[int]) -> List[int]:
        with self.lock:
            assert isinstance(self.spi, periphery.SPI), "spi interface is not initialized"
            data_in = self.spi.transfer(data_out)
        return data_in

    def leds_get(self) -> List[Any]:
        """
        returns: led_state, led_value
        """
        data_out = [
            commands.COMMAND_LEDS_GET,
            0x00, 0x00]

        data_in = self.transfer(data_out)
        if data_in[1] == 0x01:
            state = False
        elif data_in[1] == 0x02:
            state = True
        else:
            state = None
        led_value = data_in[2]
        return [state, led_value]

    def leds_status_set(self, state: bool):
        """

        """
        data_out = [
            commands.COMMAND_LEDS_STATUS_SET,
            0x2 if state else 0x1,
            0x00]
        data_in = self.transfer(data_out)
        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def leds_value_set(self, value: int):
        data_out = [
            commands.COMMAND_LEDS_VALUE_SET,
            set_byte_range(value),
            0x00]
        data_in = self.transfer(data_out)
        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def feeder_get_controller_ids(self) -> List[Any]:
        # TODO: hardcoded values should be changed to commands
        return [1, 2]

    def feeder_get_servo_angle(self, controller_id: int) -> List[Any]:
        data_out = [
            commands.COMMAND_FEEDER_GET_SERVO_ANGLE,
            controller_id,
            0x00, 0x00, 0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"
        feeder_box_angle = data_in[3]
        feeder_gate_angle = data_in[4]
        return [feeder_box_angle, feeder_gate_angle]

    def feeder_box_get_servo_open_close_angles(self, controller_id: int) -> List[Any]:
        data_out = [
            commands.COMMAND_FEEDER_BOX_GET_SERVO_OPEN_CLOSE_ANGLES,
            controller_id,
            0x00, 0x00, 0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"
        feeder_box_open_angle = data_in[3]
        feeder_box_close_angle = data_in[4]
        return [feeder_box_open_angle, feeder_box_close_angle]

    def feeder_box_set_servo_open_close_angles(self, controller_id: int, feeder_box_open_angle: int, feeder_box_close_angle: int):
        data_out = [
            commands.COMMAND_FEEDER_BOX_SET_SERVO_OPEN_CLOSE_ANGLES,
            controller_id,
            set_byte_range(feeder_box_open_angle),
            set_byte_range(feeder_box_close_angle),
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[3] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[4] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def feeder_gate_get_servo_open_close_angles(self, controller_id: int) -> List[Any]:
        data_out = [
            commands.COMMAND_FEEDER_GATE_GET_SERVO_OPEN_CLOSE_ANGLES,
            controller_id,
            0x00, 0x00, 0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"
        feeder_gate_open_angle = data_in[3]
        feeder_gate_close_angle = data_in[4]
        return [feeder_gate_open_angle, feeder_gate_close_angle]

    def feeder_gate_set_servo_open_close_angles(self, controller_id: int, feeder_gate_open_angle: int, feeder_gate_close_angle: int):
        data_out = [
            commands.COMMAND_FEEDER_GATE_SET_SERVO_OPEN_CLOSE_ANGLES,
            controller_id,
            set_byte_range(feeder_gate_open_angle),
            set_byte_range(feeder_gate_close_angle),
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[3] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[4] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def feeder_box_open(self, controller_id: int):
        data_out = [
            commands.COMMAND_FEEDER_BOX_OPEN,
            controller_id,
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, f"RESPONSE_SELECT_ERROR: {data_in[1]}"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, f"RESPONSE_PROCESSING_ERROR: {data_in[2]}"

    def feeder_box_close(self, controller_id: int):
        data_out = [
            commands.COMMAND_FEEDER_BOX_CLOSE,
            controller_id,
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def feeder_box_set_angle(self, controller_id: int, angle: int):
        data_out = [
            commands.COMMAND_FEEDER_BOX_SET_ANGLE,
            controller_id,
            set_byte_range(angle),
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "COMMAND_RESPONSE_ARGUMENT_ERROR"
        assert data_in[3] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def feeder_gate_feed(self, controller_id: int):
        data_out = [
            commands.COMMAND_FEEDER_GATE_FEED,
            controller_id,
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def feeder_gate_feed_ms(self, controller_id: int, ms: int):
        data_out = [
            commands.COMMAND_FEEDER_GATE_FEED_MS,
            controller_id,
            *int2bytes(ms),
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[3] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[4] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def feeder_gate_set_angle(self, controller_id: int, angle: int):
        data_out = [
            commands.COMMAND_FEEDER_GATE_SET_ANGLE,
            controller_id,
            set_byte_range(angle),
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[3] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def feeder_gate_open(self, controller_id: int):
        data_out = [
            commands.COMMAND_FEEDER_GATE_OPEN,
            controller_id,
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def feeder_gate_close(self, controller_id: int):
        data_out = [
            commands.COMMAND_FEEDER_GATE_CLOSE,
            controller_id,
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def drinker_get_controller_ids(self) -> List[Any]:
        # TODO: hardcoded values should be changed to commands
        return [1, 2]

    def drinker_get_params(self, controller_id: int) -> List[Any]:
        data_out = [
            commands.COMMAND_DRINKER_GET_PARAMS,
            controller_id,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"
        drinker_input_angle = data_in[3]
        drinker_output_angle = data_in[4]
        drinker_water_level_current = data_in[5]
        drinker_empty_flag = data_in[6]
        drinker_fill_flag = data_in[7]

        if drinker_empty_flag == 0x01:
            drinker_empty_flag = False
        elif drinker_empty_flag == 0x02:
            drinker_empty_flag = True
        else:
            drinker_empty_flag = None

        if drinker_fill_flag == 0x01:
            drinker_fill_flag = False
        elif drinker_fill_flag == 0x02:
            drinker_fill_flag = True
        else:
            drinker_fill_flag = None
        return [
            drinker_input_angle,
            drinker_output_angle,
            drinker_water_level_current,
            drinker_empty_flag,
            drinker_fill_flag
        ]

    def drinker_input_get_servo_open_close_angles(self, controller_id: int) -> List[Any]:
        data_out = [
            commands.COMMAND_DRINKER_INPUT_GET_OPEN_CLOSE_ANGLES,
            controller_id,
            0x00, 0x00, 0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"
        drinker_input_open_angle = data_in[3]
        drinker_input_close_angle = data_in[4]
        return [drinker_input_open_angle, drinker_input_close_angle]

    def drinker_input_set_servo_open_close_angles(self, controller_id: int, drinker_input_open_angle: int, drinker_input_close_angle: int):
        data_out = [
            commands.COMMAND_DRINKER_INPUT_SET_OPEN_CLOSE_ANGLES,
            controller_id,
            set_byte_range(drinker_input_open_angle),
            set_byte_range(drinker_input_close_angle),
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[3] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[4] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def drinker_output_get_servo_open_close_angles(self, controller_id: int) -> List[Any]:
        data_out = [
            commands.COMMAND_DRINKER_OUTPUT_GET_OPEN_CLOSE_ANGLES,
            controller_id,
            0x00, 0x00, 0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"
        drinker_output_open_angle = data_in[3]
        drinker_output_close_angle = data_in[4]
        return [drinker_output_open_angle, drinker_output_close_angle]

    def drinker_output_set_servo_open_close_angles(self, controller_id: int, drinker_output_open_angle: int, drinker_output_close_angle: int):
        data_out = [
            commands.COMMAND_DRINKER_OUTPUT_SET_OPEN_CLOSE_ANGLES,
            controller_id,
            set_byte_range(drinker_output_open_angle),
            set_byte_range(drinker_output_close_angle),
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[3] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[4] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def drinker_water_level_get_params(self, controller_id: int) -> List[Any]:
        data_out = [
            commands.COMMAND_DRINKER_WATER_LEVEL_GET_PARAMS,
            controller_id,
            0x00, 0x00, 0x00, 0x00, 0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"
        water_level_measure_iterations = data_in[3]
        water_level_max_cm_distance = data_in[4]
        water_level_max_level = data_in[5]
        water_level_min_level = data_in[6]
        if water_level_max_level == 0xff:
            water_level_max_level = -1
        if water_level_min_level == 0xff:
            water_level_min_level = -1
        return [
            water_level_measure_iterations,
            water_level_max_cm_distance,
            water_level_max_level,
            water_level_min_level
        ]

    def drinker_water_level_set_params(self, controller_id: int,
                                       water_level_measure_iterations: int,
                                       water_level_max_cm_distance: int,
                                       water_level_max_level: int,
                                       water_level_min_level: int) -> List[Any]:
        data_out = [
            commands.COMMAND_DRINKER_WATER_LEVEL_SET_PARAMS,
            controller_id,
            set_byte_range(water_level_measure_iterations),
            set_byte_range(water_level_max_cm_distance),
            0xff if water_level_max_level == -1 else set_byte_range(water_level_max_level),
            0xff if water_level_min_level == -1 else set_byte_range(water_level_min_level),
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[3] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[4] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[5] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[6] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def drinker_water_level_get_moving_average(self, controller_id: int) -> int:
        data_out = [
            commands.COMMAND_DRINKER_WATER_LEVEL_GET_MOVING_AVERAGE,
            controller_id,
            0x00, 0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"
        drinker_water_level_moving_average = data_in[3]
        return drinker_water_level_moving_average

    def drinker_input_open(self, controller_id: int):
        data_out = [
            commands.COMMAND_DRINKER_INPUT_OPEN,
            controller_id,
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def drinker_input_close(self, controller_id: int):
        data_out = [
            commands.COMMAND_DRINKER_INPUT_CLOSE,
            controller_id,
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def drinker_input_set_angle(self, controller_id: int, angle: int):
        data_out = [
            commands.COMMAND_DRINKER_INPUT_SET_ANGLE,
            controller_id,
            set_byte_range(angle),
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[3] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def drinker_output_open(self, controller_id: int):
        data_out = [
            commands.COMMAND_DRINKER_OUTPUT_OPEN,
            controller_id,
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def drinker_output_close(self, controller_id: int):
        data_out = [
            commands.COMMAND_DRINKER_OUTPUT_CLOSE,
            controller_id,
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def drinker_output_set_angle(self, controller_id: int, angle: int):
        data_out = [
            commands.COMMAND_DRINKER_OUTPUT_SET_ANGLE,
            controller_id,
            set_byte_range(angle),
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "RESPONSE_ARGUMENT_ERROR"
        assert data_in[3] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def drinker_fill(self, controller_id: int):
        data_out = [
            commands.COMMAND_DRINKER_FILL,
            controller_id,
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def drinker_empty(self, controller_id: int):
        data_out = [
            commands.COMMAND_DRINKER_EMPTY,
            controller_id,
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def drinker_reset(self, controller_id: int):
        data_out = [
            commands.COMMAND_DRINKER_RESET,
            controller_id,
            0x00]
        data_in = self.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def controller_reset(self):
        data_out = [
            commands.COMMAND_CONTROLLER_RESET,
            commands.COMMAND_CONTROLLER_RESET,
            commands.COMMAND_CONTROLLER_RESET
        ]
        data_in = self.transfer(data_out)
        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_ARGUMENT_SUCCESS, "COMMAND_RESPONSE_ARGUMENT_ERROR"


controller_api: ControllerApi = ControllerApi()
