
import board

from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

from src.hardware.common import Valve, ActionServo
from src.hardware.water_sensor import WaterLevel, WaterSensor
from src.hardware.drinker import Drinker
from src.hardware.feeder import Feeder


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

        self.pop_feed = ActionServo(self.servo0, 125, 90, 0.35)
        self.pop_box = ActionServo(self.servo1, 170, 95, 2)
        self.pop_feeder = Feeder(self.pop_box, self.pop_feed)

        self.pek_feed = ActionServo(self.servo4, 125, 90, 0.40)
        self.pek_box = ActionServo(self.servo5, 30, 100, 2)
        self.pek_feeder = Feeder(self.pek_box, self.pek_feed)

    def __del__(self):
        self.i2c.deinit()

