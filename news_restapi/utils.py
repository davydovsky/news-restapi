from datetime import datetime


def datetime_to_timestamp(dt: datetime) -> int:
    """
    Converts a datetime instance to a timestamp
    :param dt: datetime instance (local time zone)
    :return: timestamp in microseconds
    """
    return int(dt.timestamp() * 1000000)


def timestamp_to_datetime(ts: int) -> datetime:
    """
    Converts a timestamp to a datetime instance
    :param ts: timestamp in microseconds
    :return: datetime instance (local time zone)
    """
    return datetime.fromtimestamp(ts / 1e6)
