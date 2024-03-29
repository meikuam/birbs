import asyncio
from typing import List, Callable, Tuple, Literal, Any
import datetime

import cv2
import enum
import numpy as np
from src.camera.camera import camera_streams_container
from src.time.time import local_today, local_now, time2datetime, timedelta2time
from src.web.models.automatic import AutomaticDrinker, AutomaticFeeder
from src.controller.controller_api import controller_api
from src.telegram_bot.bot import chat_ids, broadcast_image, broadcast_message


async def log_message(prefix: str, message: str):
    try:
        print(f"{prefix}  {message}")
        await broadcast_message(
            chat_ids=chat_ids,
            text=f"{prefix} {message}"
        )
    except Exception as e:
        print(prefix, message, e)


async def log_image(image: np.ndarray,  caption: str = None):
    try:
        await broadcast_image(
            chat_ids=chat_ids,
            image=image,
            caption=caption
        )
    except Exception as e:
        print("log_image error:", e)


def get_frame_from_stream(controller_id: int, device_type: Literal["feeder", "drinker"]):
    device_id = camera_streams_container.device_mapping[controller_id][device_type]
    stream_select_state = camera_streams_container.select_stream(device_id)
    if stream_select_state:
        return next(camera_streams_container.get_frame(encode=False))
    else:
        return None


async def log_stream_frame(controller_id: int, device_type: Literal["feeder", "drinker"], alt_text: str = None):
    frame = get_frame_from_stream(controller_id=controller_id, device_type=device_type)
    if frame is not None:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        await log_image(frame, caption=alt_text)
    else:
        if alt_text:
            await log_message(prefix=f"{device_type} [{controller_id}]", message=alt_text)


class AutomaticUpdater:
    async def routine(self):
        raise NotImplementedError("routine not implemented")

    async def update_state(self, new_state):
        raise NotImplementedError("update_state not implemented")


async def fill_drinker(controller_id: int, threshold_level: int, logging_status: bool):
    # чекаем уровень воды
    try:
        [
            drinker_input_angle,
            drinker_output_angle,
            drinker_water_level_current,
            drinker_empty_flag,
            drinker_fill_flag
        ] = controller_api.drinker_get_params(
            controller_id=controller_id)
    except Exception as e:
        print(f"Error: controller_api.drinker_get_params {controller_id}, {e}")
        return

    # чекаем можем ли мы затриггериться
    if drinker_water_level_current >= threshold_level:
        if not drinker_fill_flag:
            try:
                controller_api.drinker_fill(controller_id=controller_id)
            except Exception as e:
                print(f"Error: controller_api.drinker_fill {controller_id}, {e}")
            if logging_status:
                await log_message(
                    prefix=f"Drinker [{controller_id}]",
                    message=f"triggered current: {drinker_water_level_current}, thresh: {threshold_level}"
                )


class AutomaticDrinkerUpdater(AutomaticUpdater):

    def __init__(self, controller_id: int):
        # TODO: check if state was saved in db
        self.controller_id = controller_id
        self.state = AutomaticDrinker(
            autofill_status=False,
            logging_status=False,
            threshold_level=50,
            day_start_time=datetime.time(hour=9, minute=0),
            day_end_time=datetime.time(hour=22, minute=0)
        )
        self.fill_triggered = False

    async def routine(self):
        if self.state.autofill_status:
            local_time = local_now().time()
            if self.state.day_start_time <= local_time <= self.state.day_end_time:
                await fill_drinker(self.controller_id, self.state.threshold_level, self.state.logging_status)

    async def update_state(self, new_state: AutomaticDrinker):
        if new_state.autofill_status is not None:
            self.state.autofill_status = new_state.autofill_status
        if new_state.logging_status is not None:
            self.state.logging_status = new_state.logging_status
        if new_state.threshold_level is not None:
            self.state.threshold_level = new_state.threshold_level
        print("state updated: ", self.state)


class TriggerState(enum.Enum):
    not_triggered = 0
    triggering = 1
    triggered = 2


async def empty_feeder(controller_id: int, logging_status: bool):
    if logging_status:
        await log_stream_frame(
            controller_id=controller_id,
            device_type="feeder",
            alt_text="empty_feeder (before empty)")
    print(local_now().time(), "feeder box open")
    controller_api.feeder_box_open(controller_id=controller_id)
    await asyncio.sleep(5)

    if logging_status:
        await log_stream_frame(
            controller_id=controller_id,
            device_type="feeder",
            alt_text="empty_feeder (after box open)")
    print(local_now().time(), "feeder box close")
    controller_api.feeder_box_close(controller_id=controller_id)
    await asyncio.sleep(5)

    if logging_status:
        await log_stream_frame(
            controller_id=controller_id,
            device_type="feeder",
            alt_text="empty_feeder (after box close)")


async def fill_feeder(controller_id: int, feed_amount: int, logging_status: bool):
    if logging_status:
        await log_stream_frame(
            controller_id=controller_id,
            device_type="feeder",
            alt_text="fill_feeder (before feed)")

    for i in range(feed_amount):
        print(local_now().time(), "feeder gate feed")
        controller_api.feeder_gate_feed(controller_id=controller_id)
        await asyncio.sleep(5)
        if logging_status:
            await log_stream_frame(
                controller_id=controller_id,
                device_type="feeder",
                alt_text=f"fill_feeder (after feed {i})")


class TimeTrigger:

    def __init__(self, trigger_time: datetime.time, func: Callable, args: Tuple[Any]):
        self.trigger_time = trigger_time
        self.func = func
        self.args = args
        self.state = TriggerState.not_triggered

    async def check_trigger(self):
        if self.state == TriggerState.not_triggered:
            local_time = local_now().time()
            if local_time > self.trigger_time:
                print("triggered ", local_time)
                self.state = TriggerState.triggering
                if asyncio.iscoroutinefunction(self.func):
                    await self.func(*self.args)
                else:
                    self.func(*self.args)
                self.state = TriggerState.triggered


class AutomaticFeederUpdater(AutomaticUpdater):

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
        self.feed_triggers: List[TimeTrigger] = []
        self.update_feed_times()

    async def routine(self):
        if self.state.autofeed_status:
            local_time = local_now().time()
            # print("start", self.state.day_start_time, "end", self.state.day_end_time, "curr", local_time)
            if self.state.day_start_time <= local_time <= self.state.day_end_time:
                # print(local_time, "check triggers")
                for trigger in self.feed_triggers:
                    # check if trigger not triggered
                    # print(trigger.state, trigger.trigger_time)
                    if trigger.state != TriggerState.triggered:
                        # check trigger
                        await trigger.check_trigger()
                        # if trigger state not changed to triggered we don't check next triggers
                        if trigger.state != TriggerState.triggered:
                            break
            else:
                # print(local_time, "reset triggers")
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
        print("state updated: ", self.state, self.feed_times)

    def update_feed_times(self):
        # print("time delta ", time2datetime(self.state.day_end_time) - time2datetime(self.state.day_start_time))
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
                args=(self.controller_id, self.state.logging_status, )),
            TimeTrigger(
                trigger_time=self.state.day_start_time,
                func=fill_feeder,
                args=(self.controller_id, self.state.feed_amount, self.state.logging_status, ))
        ]
        for i in range(self.state.daily_feed_amount - 1):
            feed_time = (time2datetime(feed_times[-1]) + tdelta_feeds).time()
            feed_times.append(feed_time)
            feed_triggers.append(
                TimeTrigger(
                    trigger_time=feed_time,
                    func=fill_feeder,
                    args=(self.controller_id, self.state.feed_amount, self.state.logging_status, ))
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
            await asyncio.sleep(1)


blade_runner = AutomaticRunner()
