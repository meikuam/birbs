import asyncio
from typing import Callable, Literal, Any, Optional
import datetime
from pydantic import BaseModel
import logging

import cv2
import enum
import numpy as np
from src.time.time import local_today, local_now, time2datetime, timedelta2time

from src.automatic.common import AutomaticUpdater, TriggerState, TimeTrigger

from src.camera.container import CameraStreamsContianer
from src.automatic.camera_logging import CameraTelegramLogging
from src.hardware.birbs import Birbs

logger = logging.getLogger(name=__name__)


birbs = Birbs()
camera_container = CameraStreamsContianer()
camera_telegram_logger = CameraTelegramLogging(camera_container)



async def fill_drinker(birb_id: str, logging_status: bool):
    if logging_status:
        await camera_telegram_logger.log_stream_frame(
            birb_id=birb_id,
            device_type="drinker",
            alt_text="fill drinker (before empty)"
        )

    logger.info(f"{local_now().time()} {birb_id} drinker fill")
    if birb_id == "pek":
        birbs.pek_drinker.fill()
    elif birb_id == "pop":
        birbs.pop_drinker.fill()

    await asyncio.sleep(5)

    if logging_status:
        await camera_telegram_logger.log_stream_frame(
            birb_id=birb_id,
            device_type="drinker",
            alt_text="fill drinker (after box open)"
        )

class AutomaticDrinker(BaseModel):
    autofill_status: Optional[bool]
    logging_status: Optional[bool]
    day_start_time: Optional[datetime.time]
    day_end_time: Optional[datetime.time]


class AutomaticDrinkerUpdater(AutomaticUpdater):

    def __init__(self, birb_id: str):
        self.birb_id = birb_id
        self.state = AutomaticDrinker(
            autofill_status=True,
            logging_status=True,
            day_start_time=datetime.time(hour=9, minute=0),
            day_end_time=datetime.time(hour=22, minute=0)
        )
        self.fill_triggered = False

    async def routine(self):
        if self.state.autofill_status:
            local_time = local_now().time()
            if self.state.day_start_time <= local_time <= self.state.day_end_time:
                await fill_drinker(self.birb_id, self.state.logging_status)

    async def update_state(self, new_state: AutomaticDrinker):
        if new_state.autofill_status is not None:
            self.state.autofill_status = new_state.autofill_status
        if new_state.logging_status is not None:
            self.state.logging_status = new_state.logging_status
        logger.info(f"state updated: {self.birb_id} {self.state}")




async def empty_feeder(birb_id: str, logging_status: bool):
    if logging_status:
        await camera_telegram_logger.log_stream_frame(
            birb_id=birb_id,
            device_type="feeder",
            alt_text="empty_feeder (before empty)"
        )

    logger.info(f"{local_now().time()} {birb_id} feeder box empty")
    if birb_id == "pek":
        birbs.pek_feeder.empty()
    elif birb_id == "pop":
        birbs.pop_feeder.empty()

    await asyncio.sleep(5)

    if logging_status:
        await camera_telegram_logger.log_stream_frame(
            birb_id=birb_id,
            device_type="feeder",
            alt_text="empty_feeder (after box open)"
        )


async def fill_feeder(birb_id: str, feed_amount: int, logging_status: bool):
    if logging_status:
        await camera_telegram_logger.log_stream_frame(
            birb_id=birb_id,
            device_type="feeder",
            alt_text="fill_feeder (before feed)"
        )

    for i in range(feed_amount):
        logger.info(f"{local_now().time()} {birb_id} feeder gate feed")

        if birb_id == "pek":
            birbs.pek_feeder.feed()
        elif birb_id == "pop":
            birbs.pop_feeder.feed()

        await asyncio.sleep(5)
        if logging_status:
            await camera_telegram_logger.log_stream_frame(
                birb_id=birb_id,
                device_type="feeder",
                alt_text=f"fill_feeder (after feed {i})"
            )


class AutomaticFeeder(BaseModel):
    autofeed_status: Optional[bool]
    logging_status: Optional[bool]
    day_start_time: Optional[datetime.time]
    day_end_time: Optional[datetime.time]
    daily_feed_amount: Optional[int]
    feed_amount: Optional[int]


class AutomaticFeederUpdater(AutomaticUpdater):

    def __init__(self, birb_id: str):
        self.birb_id = birb_id
        self.state = AutomaticFeeder(
            autofeed_status=True,
            logging_status=True,
            day_start_time=datetime.time(hour=9, minute=0),
            day_end_time=datetime.time(hour=18, minute=0),
            daily_feed_amount=3,
            feed_amount=3
        )
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


class AutomaticRunner:

    def __init__(self):
        # create drinker instances
        self.drinkers = [
            AutomaticDrinkerUpdater("pek"),
            AutomaticDrinkerUpdater("pop")
        ]
        self.feeders = [
            AutomaticFeederUpdater("pek"),
            AutomaticFeederUpdater("pop")
        ]

    async def run(self):
        while True:
            for drinker_updater in self.drinkers:
                try:
                    await drinker_updater.routine()
                except Exception as e:
                    logger.info(f"error at drinker_updater: {e}")

            for feeder_updater in self.feeders:
                try:
                    await feeder_updater.routine()
                except Exception as e:
                    logger.info(f"error at feeder_updater: {e}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    blade_runner = AutomaticRunner()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(blade_runner.run())
