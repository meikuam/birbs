import periphery


def reset_serial(devpath="/dev/ttyUSB0") -> bool:
    try:
        serial = periphery.Serial(
            devpath=devpath,
            baudrate=115200
        )
        serial.close()
        return True
    except Exception as e:
        print("reset_serial error", e)
        return False
