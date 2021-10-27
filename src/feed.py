mport serial
import pytz
from datetime import datetime, timedelta
import time
import logging





if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    # serial
    port = "/dev/ttyUSB0"
    baudrate = 115200
    timeout = 1

    ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    # feed
    time_zone = pytz.timezone("Asia/Tomsk")
    feed_time_ms = 5000
    feeder_controller_id = 1
    feed_hour = 16
    feed_minute = 30
    is_feeded_today = False
    last_feeded_time = datetime.today().astimezone(time_zone) - timedelta(days=1)
    use_feeder = True

    # led
    dawn_hour = 11
    dawn_minute = 0
    sunset_hour = 21
    sunset_minute = 0
    is_turned_on = False
    max_bridges = 190
    min_bridges = 5
    use_leds = False

    # loop
    sleep_time = 10 # seconds
    logging.info("start main loop")
    while True:
        current_date = datetime.now().astimezone(time_zone)
        # led checks
        if use_leds:
            try:
                ser.write(f"10".encode(encoding="ascii"))
                resp = ser.readline().decode(encoding="ascii")
                data = resp.split("_")
                if len(data) > 0:
                    if data[0] == "1":
                        is_turned_on = True
                    else:
                        is_turned_on = False
                dawn_date = current_date.replace(hour=dawn_hour, minute=dawn_minute, second=0, microsecond=0)
                sunset_date = current_date.replace(hour=sunset_hour, minute=sunset_minute, second=0, microsecond=0)
                if dawn_date < current_date < sunset_date and is_turned_on:
                    daytime_delta = (sunset_date - dawn_date).total_seconds()
                    current_delta = (current_date - dawn_date).total_seconds()
                    half_period = daytime_delta / 2
                    if current_delta < half_period:
                        brightness_relative = current_delta / half_period
                    else:
                        brightness_relative = (daytime_delta - current_delta) / half_period
                    brightness = max(int(brightness_relative * max_bridges), min_bridges)
                    ser.write(f"12 {brightness}".encode(encoding="ascii"))
                    logging.info(f"led set value {brightness}")
                elif is_turned_on:
                    # turn off leds
                    ser.write(f"11 1".encode(encoding="ascii"))

            except Exception as e:
                logging.error(f"led error: {e}")
                is_turned_on = False

        # feeder checks
        if use_feeder:
            try:
                feed_date = current_date.replace(hour=feed_hour, minute=feed_minute, second=0, microsecond=0)
                if is_feeded_today:
                    if (current_date - last_feeded_time).days > 0:
                        is_feeded_today = False
                        logging.info(f"feeder feeded_today set to False")

                if current_date > feed_date and not is_feeded_today:
                    logging.info(f"feeder start feeding")
                    resp = ser.readline().decode(encoding="ascii")
                    logging.info(resp)

                    ser.write(f"23 {feeder_controller_id} {feed_time_ms}".encode(encoding="ascii"))
                    time.sleep(feed_time_ms / 1000)

                    resp = ser.readline().decode(encoding="ascii")
                    logging.info(resp)
                    is_feeded_today = True
                    last_feeded_time = datetime.now().astimezone(time_zone)
                    logging.info(f"feeder succesful ({feed_time_ms}ms) at: {last_feeded_time}")


            except Exception as e:
                logging.error(f"feeder error: {e}")
        time.sleep(sleep_time)
