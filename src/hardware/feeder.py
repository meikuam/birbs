import logging
from src.hardware.common import ActionServo

logger = logging.getLogger(name=__name__)


class Feeder:
    def __init__(self, box: ActionServo, feeder: ActionServo):
        self.box = box
        self.feeder = feeder

    def feed(self):
        self.feeder.action()
        self.logger.info("feeder feed")

    def empty(self):
        self.box.action()
        self.logger.info("feeder empty")
