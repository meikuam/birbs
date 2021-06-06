import os
import time
import sys

# wierd trick to run as sudo
sys.path.append(os.path.join('/home/orangepi/.local', 'lib', 'python3.8', 'site-packages'))

import serial
from threading import Timer


class SerialConnection:

    def __init__(self, path="/dev/ttyUSB0", timeout=5):
        self.ser = serial.Serial(port=path, baudrate=9600, timeout=timeout)

    def write(self, data: str, add_newline=True):
        if add_newline:
            data = data + "\n\r"
        # print("write", data)
        self.ser.write(data.encode(encoding="ascii"))

    def read(self):
        data = self.ser.readline()
        # print("read", data)
        return data


class IRLedController:
    """
    commands:
        10 - get state
        10_0 - set state to 0
        11 - get led_value
        11_0 - set led_value
    responses:
        0_0 - state is 0
        1_0 - led_value is 0
    """

    def __init__(self, path="/dev/ttyUSB0", update_interval=1):
        self.serial_connection = SerialConnection(path=path)

        self.state = None
        self.value = None
        self.update_interval = update_interval
        self.timer = Timer(interval=self.update_interval, function=self.update)
        self.timer.start()

    def get_led_state(self):
        command = "10"
        self.serial_connection.write(command)
        data = self.serial_connection.read()
        assert len(data) > 0, "Returned empty answer"
        data = data.decode().strip()
        command, argument = data.split("_")
        assert command == "0", "Response of command is not 0"
        return int(argument) > 0

    def set_led_state(self, state: bool):
        argument = "1" if state else "0"
        command = "10_" + argument
        self.serial_connection.write(command)

    def get_led_value(self):
        command = "11"
        self.serial_connection.write(command)
        data = self.serial_connection.read()
        assert len(data) > 0, "Returned empty answer"
        data = data.decode().strip()
        command, argument = data.split("_")
        assert command == "1", "Response of command is not 1"
        return int(argument)

    def set_led_value(self, value: int):
        argument = min(max(0, value), 255)
        command = "11_" + str(argument)
        self.serial_connection.write(command)

    def update(self):
        try:
            self.state = ir_led_controller.get_led_state()
            self.value = ir_led_controller.get_led_value()
        except Exception as e:
            print(e)
        self.timer = Timer(interval=self.update_interval, function=self.update)
        self.timer.start()

    def __del__(self):
        self.serial_connection.ser.close()




if __name__ == "__main__":
    ir_led_controller = IRLedController()
    while True:
        try:
            print("state: ", ir_led_controller.state, "value: ", ir_led_controller.value)
        except Exception as e:
            print(e)
        time.sleep(1)
    # ir = SerialConnection()
    # while True:
    #     inp = input(">> ")
    #     if inp =="q":
    #         exit()
    #     ir.write(inp)
    #
    #     out = ''
    #     # let's wait one second before reading output (let's give device time to answer)
    #     time.sleep(2)
    #     out = ir.read()
    #     # while ir.ser.inWaiting() > 0:
    #     #     out += str(ir.ser.read(1))
    #
    #     if out != '':
    #         print(out)
    #
    #     # data = ir.read()
    #     # if len(data) > 0:
    #     #     print(data)
    #     # time.sleep(1)
