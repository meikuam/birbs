from typing import List, Optional
import datetime
from pydantic import BaseModel


class AutomaticDrinker(BaseModel):
    autofill_status: Optional[bool]
    logging_status: Optional[bool]
    threshold_level: Optional[int]


class AutomaticFeeder(BaseModel):
    autofeed_status: Optional[bool]
    logging_status: Optional[bool]
    day_start_time: Optional[datetime.time]
    day_end_time: Optional[datetime.time]
    daily_feed_amount: Optional[int]
    feed_amount: Optional[int]


class AutomaticFeederFeedTimes(BaseModel):
    feed_times: List[datetime.time]
