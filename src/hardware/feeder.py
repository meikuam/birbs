from src.hardware.common import ActionServo


class Feeder:
    def __init__(self, box: ActionServo, feeder: ActionServo):
        self.box = box
        self.feeder = feeder

    def feed(self):
        self.feeder.action()

    def empty(self):
        self.box.action()
