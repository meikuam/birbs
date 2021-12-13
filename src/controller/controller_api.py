from typing import List, Any
import periphery

import src.controller.commands as commands


def int2bytes(value: int) -> List[int]:
    return [(value & 0xFF00) >> 8,(value & 0xFF)]

def bytes2int(value: List[int]) -> int:
    return ((value[0] << 8) & 0xFF00) | (value[1] & 0xFF)

# data_in = spi.transfer(data_out);
class ControllerApi:

    def __init__(self, devpath="/dev/spidev1.0", max_speed=10000):
        self.spi = periphery.SPI(
            devpath=devpath,
            mode=0,
            max_speed=max_speed,
            bit_order="msb",
            bits_per_word=8)

    def leds_get(self)-> List[Any]:
        """
        returns: led_state, led_value
        """
        data_out = [commands.COMMAND_LEDS_GET, 0x00, 0x00]
        data_in = self.spi.transfer(data_out)
        if data_in[1] == 0x01:
            state = False
        elif data_in[1] == 0x02:
            state = True
        else:
            state = None
        return [state, data_in[2]]

    def leds_status_set(self, state: bool):
        """

        """
        data_out = [commands.COMMAND_LEDS_STATUS_SET, 0x2 if state else 0x1, 0x00]
        data_in = self.spi.transfer(data_out)
        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def leds_value_set(self, value: int):
        data_out = [commands.COMMAND_LEDS_VALUE_SET, max(min(value, 255), 0), 0x00]
        data_in = self.spi.transfer(data_out)
        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def feeder_get_servo_angle(self, controller_id: int) -> List[Any]:
        data_out = [commands.COMMAND_FEEDER_GET_SERVO_ANGLE, controller_id, 0x00, 0x00, 0x00]
        data_in = self.spi.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"
        feeder_box_angle = data_in[3]
        feeder_gate_angle = data_in[4]
        return [feeder_box_angle, feeder_gate_angle]

    def feeder_box_open(self, controller_id: int):
        data_out = [commands.COMMAND_FEEDER_BOX_OPEN, controller_id, 0x00]
        data_in = self.spi.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def feeder_box_close(self, controller_id: int):
        data_out = [commands.COMMAND_FEEDER_BOX_CLOSE, controller_id, 0x00]
        data_in = self.spi.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"

    def feeder_set_angle(self, controller_id: int, angle: int):
        data_out = [commands.COMMAND_FEEDER_BOX_SET_ANGLE, controller_id,  max(min(angle, 255), 0), 0x00]
        data_in = self.spi.transfer(data_out)

        assert data_in[1] == commands.COMMAND_RESPONSE_SELECT_SUCCESS, "RESPONSE_SELECT_ERROR"
        assert data_in[2] == commands.COMMAND_RESPONSE_PROCESSING_SUCCESS, "RESPONSE_PROCESSING_ERROR"
