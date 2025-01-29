import time

from adafruit_motor import servo


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


class ActionServo:
    def __init__(
        self,
        servo_drive: servo.Servo,
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
