import pytz
from datetime import datetime, timedelta


time_zone = pytz.timezone("Asia/Tomsk")


def today() -> datetime.date:
    return datetime.today().astimezone(time_zone)


def now() -> datetime.date:
    return datetime.now().astimezone(time_zone)
