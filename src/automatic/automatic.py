import sys
import asyncio
from typing import Optional
import datetime
from pydantic import BaseModel
import logging

from src.time.time import local_now, time2datetime
from src.automatic.common import AutomaticUpdater, TriggerState, TimeTrigger
from src.camera.container import CameraStreamsContianer
from src.automatic.camera_logging import CameraTelegramLogging
from src.hardware.birbs import Birbs

logger = logging.getLogger(name=__name__)


birbs = Birbs()
camera_container = CameraStreamsContianer()
camera_telegram_logger = CameraTelegramLogging(camera_container)


async def fill_drinker(birb_id: str, logging_status: bool):

    if birb_id == "pek":
        if birbs.pek_drinker.is_full():
            return False
    elif birb_id == "pop":
        if birbs.pop_drinker.is_full():
            return False

    if logging_status:
        await camera_telegram_logger.log_stream_frame(
            birb_id=birb_id,
            device_type="drinker",
            alt_text=f"{birb_id} before fill drinker"
        )

    logger.info(f"{local_now().time()} {birb_id} drinker fill")
    try:
        if birb_id == "pek":
            birbs.pek_drinker.fill()
        elif birb_id == "pop":
            birbs.pop_drinker.fill()
    except (TimeoutError, Exception) as e:
        message = f"{local_now().time()} {birb_id} drinker got error {e}"
        logger.error(message)
        if logging_status:
            await camera_telegram_logger.log_message(message)

    await asyncio.sleep(5)

    if logging_status:
        await camera_telegram_logger.log_stream_frame(
            birb_id=birb_id,
            device_type="drinker",
            alt_text=f"{birb_id} after fill drinker"
        )
    return True


async def empty_drinker(birb_id: str, logging_status: bool):
    if logging_status:
        await camera_telegram_logger.log_stream_frame(
            birb_id=birb_id,
            device_type="drinker",
            alt_text=f"{birb_id} before empty drinker"
        )

    logger.info(f"{local_now().time()} {birb_id} empty drinker 1")
    if birb_id == "pek":
        birbs.pek_drinker.empty()
    elif birb_id == "pop":
        birbs.pop_drinker.empty()

    await asyncio.sleep(5)

    logger.info(f"{local_now().time()} {birb_id} empty drinker 2")
    if birb_id == "pek":
        birbs.pek_drinker.empty()
    elif birb_id == "pop":
        birbs.pop_drinker.empty()

    await asyncio.sleep(5)

    if logging_status:
        await camera_telegram_logger.log_stream_frame(
            birb_id=birb_id,
            device_type="drinker",
            alt_text=f"{birb_id} after empty drinker"
        )


class AutomaticDrinker(BaseModel):
    autofill_status: Optional[bool]
    logging_status: Optional[bool]
    day_start_time: Optional[datetime.time]
    day_end_time: Optional[datetime.time]
    cooldown_period: Optional[datetime.timedelta]
    daily_drink_amount: Optional[datetime.timedelta]


class AutomaticDrinkerUpdater(AutomaticUpdater):

    def __init__(self, birb_id: str, state: AutomaticDrinker = None):
        self.birb_id = birb_id
        self.state = AutomaticDrinker(
            autofill_status=True,
            logging_status=True,
            day_start_time=datetime.time(hour=9, minute=0),
            day_end_time=datetime.time(hour=22, minute=0),
            cooldown_period=datetime.timedelta(hours=1, minutes=0),
            daily_drink_amount=1
        ) if state is None else state
        self.triggered_timestamp = None
        self.triggers = []
        self.times = []
        self.update_times()

    async def routine(self):
        if self.state.autofill_status:
            local_time = local_now().time()
            if self.state.day_start_time <= local_time <= self.state.day_end_time:
                for trigger in self.triggers:
                    # check if trigger not triggered
                    if trigger.state != TriggerState.triggered:
                        # check trigger
                        await trigger.check_trigger()
                        # if trigger state not changed to triggered we don't check next triggers
                        if trigger.state != TriggerState.triggered:
                            break

                if self.check_cooldown():
                    if await fill_drinker(self.birb_id, self.state.logging_status):
                        self.triggered_timestamp = local_now()
            else:
                for trigger in self.triggers:
                    trigger.state = TriggerState.not_triggered

    def check_cooldown(self):
        if self.triggered_timestamp is None:
            return True
        condition = self.triggered_timestamp + self.state.cooldown_period < local_now()
        return condition

    async def update_state(self, new_state: AutomaticDrinker):
        if new_state.autofill_status is not None:
            self.state.autofill_status = new_state.autofill_status
        if new_state.logging_status is not None:
            self.state.logging_status = new_state.logging_status
        if new_state.day_start_time is not None:
            self.state.day_start_time = new_state.day_start_time
        if new_state.day_end_time is not None:
            self.state.day_end_time = new_state.day_end_time
        if new_state.cooldown_period is not None:
            self.state.cooldown_period = new_state.cooldown_period
        if new_state.daily_drink_amount is not None:
            self.state.daily_drink_amount = new_state.daily_drink_amount
        self.update_times()
        logger.info(f"state updated: {self.birb_id} {self.state}")

    def update_times(self):
        t2 = time2datetime(self.state.day_end_time)
        t1 = time2datetime(self.state.day_start_time)
        tdelta = t2 - t1
        tdelta_drinks = tdelta / self.state.daily_drink_amount
        self.times = []
        self.triggers = []
        times = [self.state.day_start_time]
        triggers = [
            TimeTrigger(
                trigger_time=self.state.day_start_time,
                func=empty_drinker,
                args=(self.birb_id, self.state.logging_status, )),
            TimeTrigger(
                trigger_time=self.state.day_start_time,
                func=fill_drinker,
                args=(self.birb_id, self.state.logging_status, ))
        ]
        for i in range(self.state.daily_drink_amount - 1):
            drink_time = (time2datetime(times[-1]) + tdelta_drinks).time()
            times.append(drink_time)
            triggers.append(
                TimeTrigger(
                    trigger_time=drink_time,
                    func=fill_drinker,
                    args=(self.birb_id, self.state.logging_status, ))
            )

        # check if some of triggers should be triggered now
        local_time = local_now().time()
        for trigger in triggers:
            if local_time > trigger.trigger_time:
                trigger.state = TriggerState.triggered

        self.times, self.triggers = times, triggers
        logger.info(f"{self.birb_id} update_drink_times {self.times}")


async def empty_feeder(birb_id: str, logging_status: bool):
    if logging_status:
        await camera_telegram_logger.log_stream_frame(
            birb_id=birb_id,
            device_type="feeder",
            alt_text=f"{birb_id} empty_feeder (before empty)"
        )

    logger.info(f"{local_now().time()} {birb_id} feeder box empty")
    try:
        if birb_id == "pek":
            birbs.pek_feeder.empty()
        elif birb_id == "pop":
            birbs.pop_feeder.empty()
    except Exception as e:
        message = f"{local_now().time()} {birb_id} feeder got error {e}"
        logger.error(message)
        if logging_status:
            await camera_telegram_logger.log_message(message)


    await asyncio.sleep(5)

    if logging_status:
        await camera_telegram_logger.log_stream_frame(
            birb_id=birb_id,
            device_type="feeder",
            alt_text=f"{birb_id} empty_feeder (after box open)"
        )


async def fill_feeder(birb_id: str, feed_amount: int, logging_status: bool):
    if logging_status:
        await camera_telegram_logger.log_stream_frame(
            birb_id=birb_id,
            device_type="feeder",
            alt_text=f"{birb_id} fill_feeder (before feed)"
        )

    for i in range(feed_amount):
        logger.info(f"{local_now().time()} {birb_id} feeder gate feed")

        try:
            if birb_id == "pek":
                birbs.pek_feeder.feed()
            elif birb_id == "pop":
                birbs.pop_feeder.feed()
        except Exception as e:
            message = f"{local_now().time()} {birb_id} feeder got error {e}"
            logger.error(message)
            if logging_status:
                await camera_telegram_logger.log_message(message)

        await asyncio.sleep(5)
        if logging_status:
            await camera_telegram_logger.log_stream_frame(
                birb_id=birb_id,
                device_type="feeder",
                alt_text=f"{birb_id} fill_feeder (after feed {i})"
            )


class AutomaticFeeder(BaseModel):
    autofeed_status: Optional[bool]
    logging_status: Optional[bool]
    day_start_time: Optional[datetime.time]
    day_end_time: Optional[datetime.time]
    daily_feed_amount: Optional[int]
    feed_amount: Optional[int]


class AutomaticFeederUpdater(AutomaticUpdater):

    def __init__(self, birb_id: str, state: AutomaticFeeder = None):
        self.birb_id = birb_id
        self.state = AutomaticFeeder(
            autofeed_status=True,
            logging_status=True,
            day_start_time=datetime.time(hour=9, minute=0),
            day_end_time=datetime.time(hour=18, minute=0),
            daily_feed_amount=3,
            feed_amount=3
        ) if state is None else state
        self.feed_times: list[datetime.time] = []
        self.feed_triggers: list[TimeTrigger] = []
        self.update_feed_times()

    async def routine(self):
        if self.state.autofeed_status:
            local_time = local_now().time()
            if self.state.day_start_time <= local_time <= self.state.day_end_time:
                for trigger in self.feed_triggers:
                    # check if trigger not triggered
                    if trigger.state != TriggerState.triggered:
                        # check trigger
                        await trigger.check_trigger()
                        # if trigger state not changed to triggered we don't check next triggers
                        if trigger.state != TriggerState.triggered:
                            break
            else:
                for trigger in self.feed_triggers:
                    trigger.state = TriggerState.not_triggered

    async def update_state(self, new_state: AutomaticFeeder):
        if new_state.autofeed_status is not None:
            self.state.autofeed_status = new_state.autofeed_status
        if new_state.logging_status is not None:
            self.state.logging_status = new_state.logging_status
        if new_state.day_start_time is not None:
            self.state.day_start_time = new_state.day_start_time
        if new_state.day_end_time is not None:
            self.state.day_end_time = new_state.day_end_time
        if new_state.daily_feed_amount is not None:
            self.state.daily_feed_amount = new_state.daily_feed_amount
        if new_state.feed_amount is not None:
            self.state.feed_amount = new_state.feed_amount

        self.update_feed_times()
        logger.info(f"state updated: {self.birb_id} {self.state} {self.feed_times}")

    def update_feed_times(self):
        t2 = time2datetime(self.state.day_end_time)
        t1 = time2datetime(self.state.day_start_time)
        tdelta = t2 - t1
        tdelta_feeds = tdelta / self.state.daily_feed_amount

        self.feed_times, self.feed_triggers = [], []

        feed_times = [self.state.day_start_time]
        feed_triggers = [
            TimeTrigger(
                trigger_time=self.state.day_start_time,
                func=empty_feeder,
                args=(self.birb_id, self.state.logging_status, )),
            TimeTrigger(
                trigger_time=self.state.day_start_time,
                func=fill_feeder,
                args=(self.birb_id, self.state.feed_amount, self.state.logging_status, ))
        ]
        for i in range(self.state.daily_feed_amount - 1):
            feed_time = (time2datetime(feed_times[-1]) + tdelta_feeds).time()
            feed_times.append(feed_time)
            feed_triggers.append(
                TimeTrigger(
                    trigger_time=feed_time,
                    func=fill_feeder,
                    args=(self.birb_id, self.state.feed_amount, self.state.logging_status, ))
            )

        # check if some of triggers should be triggered now
        local_time = local_now().time()
        for trigger in feed_triggers:
            if local_time > trigger.trigger_time:
                trigger.state = TriggerState.triggered

        self.feed_times, self.feed_triggers = feed_times, feed_triggers
        logger.info(f"{self.birb_id} update_feed_times {self.feed_times}")


class AutomaticRunner:

    def __init__(self):
        # create drinker instances
        self.drinkers = [
            AutomaticDrinkerUpdater("pek", AutomaticDrinker(
                autofill_status=True,
                logging_status=True,
                day_start_time=datetime.time(hour=9, minute=15),
                day_end_time=datetime.time(hour=19, minute=0),
                cooldown_period=datetime.timedelta(hours=1, minutes=0),
                daily_drink_amount=1
            )),
            AutomaticDrinkerUpdater("pop", AutomaticDrinker(
                autofill_status=True,
                logging_status=True,
                day_start_time=datetime.time(hour=9, minute=18),
                day_end_time=datetime.time(hour=19, minute=0),
                cooldown_period=datetime.timedelta(hours=2, minutes=0),
                daily_drink_amount=1
            ))
        ]
        self.feeders = [
            AutomaticFeederUpdater("pek", AutomaticFeeder(
                autofeed_status=True,
                logging_status=True,
                day_start_time=datetime.time(hour=9, minute=0),
                day_end_time=datetime.time(hour=19, minute=0),
                daily_feed_amount=3,
                feed_amount=3
            )),
            AutomaticFeederUpdater("pop", AutomaticFeeder(
                autofeed_status=True,
                logging_status=True,
                day_start_time=datetime.time(hour=9, minute=5),
                day_end_time=datetime.time(hour=18, minute=0),
                daily_feed_amount=3,
                feed_amount=3
            ))
        ]

    async def run(self):
        while True:
            for drinker_updater in self.drinkers:
                try:
                    await drinker_updater.routine()
                except Exception as e:
                    logger.error(f"error at drinker_updater: {e}")

            for feeder_updater in self.feeders:
                try:
                    await feeder_updater.routine()
                except Exception as e:
                    logger.error(f"error at feeder_updater: {e}")
            await asyncio.sleep(60)


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    blade_runner = AutomaticRunner()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(blade_runner.run())
