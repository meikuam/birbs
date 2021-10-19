import os
import time
import sys

sys.path.append(os.path.join('/home/orangepi/.local/lib/python3.8/site-packages'))

import serial
from threading import Timer


class SerialConnection:

    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, timeout=5):
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def write(self, data: str, add_newline=False):
        if add_newline:
            data = data + "\n\r"
#        print("data", data)
        self.ser.write(data.encode(encoding="ascii"))
#        print("sended")

    def read(self):
#        print("read")
        data = self.ser.readline()
        data = data.decode(encoding="ascii")
#        print("data", data)
        return data

# TODO: move serialconnection to controller classes, add mutex to read/write operations, add boudaries
class LedController:

    def __init__(self):
        self.led_state = None
        self.led_value = None

    def get(self, ser):
        ser.write("10")
        data = ser.read()
        data = data.split("_")
        if len(data) > 1:
            self.led_state = int(data[0])
            self.led_value = int(data[1])
            return True
        else:
            return False

    def set_led_state(self, ser, state: bool):
        if state:
            state = 2
        else:
            state = 1
        command = f"11 {state}"
        ser.write(command)

    def set_led_value(self, ser, value: int):
        command = f"12 {value}"
        ser.write(command)


class ServoController:
    def __init__(self, angle_close: int, angle_open: int):
        self.angle_close = angle_close
        self.angle_open = angle_open
        self.current_angle = -1


class FeederController:

    def __init__(self, controller_id=1):
        self.controller_id = controller_id
        self.box_controller = ServoController(angle_close=100, angle_open=30)
        self.feeder_motor_delay = 5000

    def get(self, ser):
        command = f"20 {self.controller_id}"
        ser.write(command)
        data = ser.read()
        data = data.split("_")
        if len(data) > 1:
            self.box_controller.current_angle = int(data[1])
            return True
        else:
            return False

    def box_open(self, ser):
        self.box_set_angle(ser, self.box_controller.angle_open)

    def box_close(self, ser):
        self.box_set_angle(ser, self.box_controller.angle_close)

    def box_set_angle(self, ser, angle):
        command = f"21 {self.controller_id} {angle}"
        ser.write(command)

    def feed(self, ser, delay=None):
        if delay is None:
            delay = self.feeder_motor_delay
        command = f"23 {self.controller_id} {delay}"
        ser.write(command)


class DrinkerController:

    def __init__(self, controller_id=1):
        self.controller_id = controller_id
        self.input_controller = ServoController(angle_close=150, angle_open=60)
        self.output_controller = ServoController(angle_close=135, angle_open=60)

    def get(self, ser):
        command = f"30 {self.controller_id}"
        ser.write(command)
        data = ser.read()
        data = data.split("_")
        if len(data) > 1:
            self.input_controller.current_angle = int(data[1])
            self.output_controller.current_angle = int(data[2])
            return True
        else:
            return False

    def input_open(self, ser):
        self.input_set_angle(ser, self.input_controller.angle_open)

    def input_close(self, ser):
        self.input_set_angle(ser, self.input_controller.angle_close)

    def input_set_angle(self, ser, angle):
        command = f"31 {self.controller_id} {angle}"
        ser.write(command)

    def output_open(self, ser):
        self.output_set_angle(ser, self.output_controller.angle_open)

    def output_close(self, ser):
        self.output_set_angle(ser, self.output_controller.angle_close)

    def output_set_angle(self, ser, angle):
        command = f"32 {self.controller_id} {angle}"
        ser.write(command)


class BirdsController:

    def __init__(self, port="/dev/ttyUSB0", update_interval=1):
        self.serial_connection = SerialConnection(port=port)
        self.led_controller = LedController()
        self.feeder_controllers = [
            FeederController(1),
            FeederController(2)
        ]
        self.drinker_controllers = [
            DrinkerController(1),
            DrinkerController(2)
        ]

    def get(self, verbose=True):
        self.led_controller.get(self.serial_connection)
        for feeder_controller in self.feeder_controllers:
            feeder_controller.get(self.serial_connection)
        for drinker_controller in self.drinker_controllers:
            drinker_controller.get(self.serial_connection)
        if verbose:
            print("led_controller:")
            print(f"\tstate: {self.led_controller.led_state}")
            print(f"\tvalue: {self.led_controller.led_value}")
            for feeder_controller in self.feeder_controllers:
                print(f"feeder_controller[{feeder_controller.controller_id}]:")
                print(f"\tbox_angle: {feeder_controller.box_controller.current_angle}")
            for drinker_controller in self.drinker_controllers:
                print(f"drinker_controller[{drinker_controller.controller_id}]:")
                print(f"\tinput_angle: {drinker_controller.input_controller.current_angle}")
                print(f"\toutput_angle: {drinker_controller.output_controller.current_angle}")



if __name__ == "__main__":

    birds_controller = BirdsController()
    while True:
        birds_controller.feeder_controllers[0].feed(birds_controller.serial_connection, 1000)
        time.sleep(100)
        birds_controller.drinker_controllers[0].input_open(birds_controller.serial_connection)
        time.sleep(100)
        birds_controller.drinker_controllers[0].input_close(birds_controller.serial_connection)

        try:
            birds_controller.get()

        except Exception as e:
            print(e)
        time.sleep(5)
