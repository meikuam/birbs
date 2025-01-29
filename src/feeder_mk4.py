import time
import board

from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
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


class Valve:
    def __init__(
        self,
        servo_drive: servo.Servo,
        open_angle: int,
        close_angle: int
    ):
        self.servo_drive = servo_drive
        self.open_angle = open_angle
        self.close_angle = close_angle
        self.wait_time = 1
    def open(self):
        self.servo_drive.angle = self.open_angle
        time.sleep(self.wait_time)
        self.servo_drive.fraction = None
    def close(self):
        self.servo_drive.angle = self.close_angle
        time.sleep(self.wait_time)
        self.servo_drive.fraction = None


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

class ActionDrive:
    def __init__(
        self,
        servo_drive,
        open_angle: int,
        close_angle: int,
        action_delay: float,
        post_action_delay: float = 0.2
    ):
        self.servo_drive = servo_drive
        self.open_angle = open_angle
        self.close_angle = close_angle
        self.action_delay = action_delay
        self.post_action_delay = post_action_delay
    def action(self):
        self.servo_drive.angle = self.open_angle
        time.sleep(self.action_delay)
        self.servo_drive.angle = self.close_angle
        time.sleep(self.post_action_delay)
        self.servo_drive.fraction = None



class Feeder:
    def __init__(self, box: ActionDrive, feeder: ActionDrive):
        self.box = box
        self.feeder = feeder
    def feed(self):
        self.feeder.action()
    def empty(self):
        self.box.action()


class Birbs:
    def __init__(self):
        self.i2c = board.I2C()
        self.water_level = WaterLevel(self.i2c)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50
        self.servo0 = servo.Servo(self.pca.channels[0], min_pulse=500, max_pulse=2500)  # попуги подача открыто 125 закрыто 90
        self.servo1 = servo.Servo(self.pca.channels[1], min_pulse=500, max_pulse=2500)  # попуги дно открыто 50 закрыто 90
        self.servo4 = servo.Servo(self.pca.channels[4], min_pulse=500, max_pulse=2500)  # пеки подача октрыто 125 закрыто 90
        self.servo5 = servo.Servo(self.pca.channels[5], min_pulse=500, max_pulse=2500)  # пеки дно открыто 50 закрыто 110
        self.servo12 = servo.Servo(self.pca.channels[12], min_pulse=500, max_pulse=2500)  # попуги подача 145 закрыто 60 открыто
        self.servo15 = servo.Servo(self.pca.channels[15], min_pulse=500, max_pulse=2500)  # попуги канализация 130 закрыто 40 открыто
        self.servo13 = servo.Servo(self.pca.channels[13], min_pulse=500, max_pulse=2500)  # пеки подача 145 закрыто 60 открыто
        self.servo14 = servo.Servo(self.pca.channels[14], min_pulse=500, max_pulse=2500)  # пеки канализация 120 закрыто 40 открыто

        self.pek_in_valve = Valve(self.servo13, 60, 145)
        self.pek_out_valve = Valve(self.servo14, 40, 120)
        self.pek_water_sensor = WaterSensor(self.water_level, 1, 70, 65)
        self.pek_drinker = Drinker(self.pek_in_valve, self.pek_out_valve, self.pek_water_sensor)

        self.pop_in_valve = Valve(self.servo12, 60, 145)
        self.pop_out_valve = Valve(self.servo15, 40, 120)
        self.pop_water_sensor = WaterSensor(self.water_level, 0, 70, 65)
        self.pop_drinker = Drinker(self.pop_in_valve, self.pop_out_valve, self.pop_water_sensor)

        self.pop_feed = ActionDrive(self.servo0, 125, 90, 0.35)
        self.pop_box = ActionDrive(self.servo1, 170, 95, 2)
        self.pop_feeder = Feeder(self.pop_box, self.pop_feed)

        self.pek_feed = ActionDrive(self.servo4, 125, 90, 0.40)
        self.pek_box = ActionDrive(self.servo5, 30, 100, 2)
        self.pek_feeder = Feeder(self.pek_box, self.pek_feed)

    def __del__(self):
        self.i2c.deinit()



if __name__ == "__main__":
    # i2c = board.I2C()

    # water_level = WaterLevel(i2c)

    # pca = PCA9685(i2c)
    # pca.frequency = 50

    # servo0 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500)  # попуги подача открыто 125 закрыто 90
    # servo1 = servo.Servo(pca.channels[1], min_pulse=500, max_pulse=2500)  # попуги дно открыто 50 закрыто 90

    # servo4 = servo.Servo(pca.channels[4], min_pulse=500, max_pulse=2500)  # пеки подача октрыто 125 закрыто 90
    # servo5 = servo.Servo(pca.channels[5], min_pulse=500, max_pulse=2500)  # пеки дно открыто 50 закрыто 110

    # servo12 = servo.Servo(pca.channels[12], min_pulse=500, max_pulse=2500)  # попуги подача 145 закрыто 60 открыто
    # servo15 = servo.Servo(pca.channels[15], min_pulse=500, max_pulse=2500)  # попуги канализация 130 закрыто 40 открыто

    # servo13 = servo.Servo(pca.channels[13], min_pulse=500, max_pulse=2500)  # пеки подача 145 закрыто 60 открыто
    # servo14 = servo.Servo(pca.channels[14], min_pulse=500, max_pulse=2500)  # пеки канализация 120 закрыто 40 открыто


    # # у пеков уровень воды макс 68 мин 70
    # # попуги макс 65 мин 70
    # pek_in_valve = Valve(servo13, 60, 145)
    # pek_out_valve = Valve(servo14, 40, 120)
    # pek_water_sensor = WaterSensor(water_level, 1, 70, 68)
    # pek_drinker = Drinker(pek_in_valve, pek_out_valve, pek_water_sensor)

    # pop_in_valve = Valve(servo12, 60, 145)
    # pop_out_valve = Valve(servo15, 40, 120)
    # pop_water_sensor = WaterSensor(water_level, 0, 70, 65)
    # pop_drinker = Drinker(pop_in_valve, pop_out_valve, pop_water_sensor)

    # pop_feeder = ActionDrive(servo0, 125, 90, 0.3)
    # pop_box = ActionDrive(servo1, 50, 90, 2)
    # pop_feed = Feeder(pop_box, pop_feeder)

    # pek_feeder = ActionDrive(servo4, 125, 90, 0.3)
    # pek_box = ActionDrive(servo5, 50, 100, 2)
    # pek_feed = Feeder(pek_box, pek_feeder)

    birbs = Birbs()


