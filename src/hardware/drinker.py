import time
import logging
from src.hardware.common import Valve
from src.hardware.water_sensor import WaterSensor

logger = logging.getLogger(name=__name__)


class Drinker:
    def __init__(
        self,
        in_valve: Valve,
        out_valve: Valve,
        water_sensor: WaterSensor,
        action_timeout: float = 5.0,
        check_period: float = 0.1
    ):
        self.water_sensor = water_sensor
        self.in_valve = in_valve
        self.out_valve = out_valve
        self.action_timeout = action_timeout
        self.check_period = check_period

    def fill(self):
        self.out_valve.close()
        action_start = time.perf_counter()
        if not self.water_sensor.is_full():
            self.in_valve.open()
        while not self.water_sensor.is_full():
            if time.perf_counter() > action_start + self.action_timeout:
                logger.info(f"drinker {self.water_sensor.sensor_id} close")
                self.in_valve.close()
                raise TimeoutError()
            time.sleep(self.check_period)
            logger.info(f"drinker {self.water_sensor.sensor_id} not full")
        self.in_valve.close()

    def empty(self):
        self.in_valve.close()
        self.out_valve.open()
        while not self.water_sensor.is_empty():
            time.sleep(self.check_period)
            logger.info(f"drinker {self.water_sensor.sensor_id} not empty")
        self.out_valve.close()
