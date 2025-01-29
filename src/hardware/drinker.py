import time
from src.hardware.common import Valve
from src.hardware.water_sensor import WaterSensor


class Drinker:
    def __init__(
        self,
        in_valve: Valve,
        out_valve: Valve,
        water_sensor: WaterSensor,
        action_timeout: int = 5
    ):
        self.water_sensor = water_sensor
        self.in_valve = in_valve
        self.out_valve = out_valve
        self.action_timeout = action_timeout

    def fill(self):
        self.out_valve.close()
        action_start = time.perf_counter()
        if not self.water_sensor.is_full():
            self.in_valve.open()
        while not self.water_sensor.is_full():
            if time.perf_counter() > action_start + self.action_timeout:
                print("close")
                self.in_valve.close()
                raise TimeoutError()
            time.sleep(0.1)
            print("not full")
        self.in_valve.close()

    def empty(self):
        self.in_valve.close()
        self.out_valve.open()
        while not self.water_sensor.is_empty():
            time.sleep(0.1)
            print("not empty")
        self.out_valve.close()
