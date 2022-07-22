import asyncio
from typing import List
import datetime

from src.time.time import local_today, local_now, time2datetime, timedelta2time
from src.web.models.automatic import AutomaticDrinker, AutomaticFeeder
from src.controller.controller_api import controller_api
from src.telegram_bot.bot import chat_ids, broadcast_image, broadcast_message


class AutomaticUpdater:
    async def routine(self):
        raise NotImplementedError("routine not implemented")

    async def update_state(self, new_state):
        raise NotImplementedError("update_state not implemented")


class AutomaticDrinkerUpdater:

    def __init__(self, controller_id: int):
        # TODO: check if state was saved in db
        self.controller_id = controller_id
        self.state = AutomaticDrinker(
            autofill_status=False,
            logging_status=False,
            threshold_level=50
        )

    async def routine(self):
        if self.state.autofill_status:
            print("automatic drinker triggered", local_now(), self.state)
            if self.state.logging_status:
                await broadcast_message(chat_ids=chat_ids, text=f"auto drinker triggered {self.controller_id}")


        await asyncio.sleep(30)

    async def update_state(self, new_state: AutomaticDrinker):
        # TODO: we can check new state better
        if new_state.autofill_status is not None:
            self.state.autofill_status = new_state.autofill_status
        if new_state.logging_status is not None:
            self.state.logging_status = new_state.logging_status
        if new_state.threshold_level is not None:
            self.state.threshold_level = new_state.threshold_level
        print("state updated: ", self.state)


class AutomaticFeederUpdater:

    def __init__(self, controller_id: int):
        # TODO: check if state was saved in db
        self.controller_id = controller_id
        self.state = AutomaticFeeder(
            autofeed_status=False,
            logging_status=False,
            day_start_time=datetime.time(hour=9, minute=0),
            day_end_time=datetime.time(hour=18, minute=0),
            daily_feed_amount=3,
            feed_amount=3
        )
        self.feed_times: List[datetime.time] = []
        self.update_feed_times()

    async def routine(self):
        if self.state.autofeed_status:
            print("automatic feeder triggered", local_now(), self.state)
            if self.state.logging_status:
                await broadcast_message(chat_ids=chat_ids, text=f"auto feeder triggered {self.controller_id}")

        await asyncio.sleep(30)

    async def update_state(self, new_state: AutomaticFeeder):
        # TODO: we can check new state better
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
            self.update_feed_times()
        if new_state.feed_amount is not None:
            self.state.feed_amount = new_state.feed_amount
        print("state updated: ", self.state)

    def update_feed_times(self):
        print("time delta ", time2datetime(self.state.day_end_time) - time2datetime(self.state.day_start_time))
        t2 = time2datetime(self.state.day_end_time)
        t1 = time2datetime(self.state.day_start_time)
        tdelta = t2 - t1
        tdelta_feeds = tdelta / self.state.daily_feed_amount
        self.feed_times = [self.state.day_start_time]
        for i in range(self.state.daily_feed_amount - 1):
            self.feed_times.append((time2datetime(self.feed_times[-1]) + tdelta_feeds).time())


class AutomaticRunner:

    def __init__(self):
        # create drinker instances
        self.drinkers = {}
        for controller_id in controller_api.drinker_get_controller_ids():
            self.drinkers[controller_id] = AutomaticDrinkerUpdater(controller_id)
        # create feeder_instances
        self.feeders = {}
        for controller_id in controller_api.feeder_get_controller_ids():
            self.feeders[controller_id] = AutomaticFeederUpdater(controller_id)

    async def run(self):
        while True:
            for controller_api, drinker_updater in self.drinkers.items():
                try:
                    await drinker_updater.routine()
                except Exception as e:
                    print("error at drinker_updater", e)
            for controller_api, feeder_updater in self.feeders.items():
                try:
                    await feeder_updater.routine()
                except Exception as e:
                    print("error at feeder_updater", e)


blade_runner = AutomaticRunner()
