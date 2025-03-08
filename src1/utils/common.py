import time


def get_timestamp() -> int:
    timestamp = int(time.time() * 1000000)
    return timestamp


def counter_gen(start=0, step=1):
    while True:
        start += step
        new_values = yield start
        if new_values is not None:
            step = new_values[1]
            start = new_values[0] - step
