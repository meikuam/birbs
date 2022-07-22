import pytz
from datetime import datetime, timedelta, time


time_zone = pytz.timezone("Asia/Tomsk")


def local_today() -> datetime.date:
    return datetime.today().astimezone(time_zone)


def local_now() -> datetime.date:
    return datetime.now().astimezone(time_zone)


def time2datetime(time: time):
    return datetime.combine(local_today(), time)


def timedelta2time(tdelta: timedelta):
    return (local_today() + tdelta).time()
