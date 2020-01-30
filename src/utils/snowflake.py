import time
import sentry_sdk
from utils.logger import log

# Nov 04 2010 01:42:54 UTC in milliseconds
twepoch = 1288834974657

# 2 ** 8 = 256;   2 ** 10 = 1024
worker_id_bits = 8
data_center_id_bits = 2
max_worker_id = -1 ^ (-1 << worker_id_bits)
max_data_center_id = -1 ^ (-1 << data_center_id_bits)
sequence_bits = 12
worker_id_shift = sequence_bits
data_center_id_shift = sequence_bits + worker_id_bits
timestamp_left_shift = sequence_bits + worker_id_bits + data_center_id_bits
sequence_mask = -1 ^ (-1 << sequence_bits)


def snowflake_to_timestamp(_id):
    _id = _id >> 22   # strip the lower 22 bits
    _id += twepoch    # adjust for twitter epoch
    _id = _id / 1000  # convert from milliseconds to seconds
    return _id


def generator(worker_id, data_center_id, sleep=lambda x: time.sleep(x/1000.0)):
    assert worker_id >= 0 and worker_id <= max_worker_id
    assert data_center_id >= 0 and data_center_id <= max_data_center_id

    last_timestamp = -1
    sequence = 0

    while True:
        timestamp = int(time.time()*1000)

        if last_timestamp > timestamp:
            log.e(f'clock is moving backwards. waiting until {last_timestamp}')
            sentry_sdk.capture_message(f'clock is moving backwards. waiting until {last_timestamp}')
            sleep(last_timestamp-timestamp)
            continue

        if last_timestamp == timestamp:
            sequence = (sequence + 1) & sequence_mask
            if sequence == 0:
                log.e('sequence overrun')
                sentry_sdk.capture_message('sequence overrun')
                sequence = -1 & sequence_mask
                sleep(1)
                continue
        else:
            sequence = 0

        last_timestamp = timestamp

        yield (
            ((timestamp-twepoch) << timestamp_left_shift) |
            (data_center_id << data_center_id_shift) |
            (worker_id << worker_id_shift) |
            sequence)
