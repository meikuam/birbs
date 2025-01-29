from adafruit_bus_device import i2c_device
from adafruit_register.i2c_struct import Struct


class WaterLevel:
    level1 = Struct(0x00, ">B")
    level2 = Struct(0x01, ">B")

    def __init__(self, i2c: i2c_device.I2CDevice, device_addr=0x62):
        self.i2c_device = i2c_device.I2CDevice(i2c, device_addr)

    def level(self, i: int):
        if i == 0:
            return self.level1
        elif i == 1:
            return self.level2


class WaterSensor:
    def __init__(
        self,
        water_level: WaterLevel,
        sensor_id: int,
        min_level: int,
        max_level: int
    ):
        self.water_level = water_level
        self.sensor_id = sensor_id
        self.min_level = min_level
        self.max_level = max_level

    @property
    def level(self):
        return self.water_level.level(self.sensor_id)[0]

    def is_empty(self):
        return self.level > self.min_level

    def is_full(self):
        return self.level < self.max_level
