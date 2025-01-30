from __future__ import annotations
import enum
import logging
import datetime
import asyncio
from typing import Callable, Any

from src.time.time import local_now


logger = logging.getLogger(name=__name__)


class AutomaticUpdater:
    async def routine(self):
        raise NotImplementedError("routine not implemented")

    async def update_state(self, new_state):
        raise NotImplementedError("update_state not implemented")


class TriggerState(enum.Enum):
    not_triggered = 0
    triggering = 1
    triggered = 2


class TimeTrigger:

    def __init__(self, trigger_time: datetime.time, func: Callable, args: tuple[Any]):
        self.trigger_time = trigger_time
        self.func = func
        self.args = args
        self.state = TriggerState.not_triggered

    async def check_trigger(self):
        if self.state == TriggerState.not_triggered:
            local_time = local_now().time()
            if local_time > self.trigger_time:
                logger.info(f"triggered: {local_time}")
                self.state = TriggerState.triggering
                if asyncio.iscoroutinefunction(self.func):
                    await self.func(*self.args)
                else:
                    self.func(*self.args)
                self.state = TriggerState.triggered
