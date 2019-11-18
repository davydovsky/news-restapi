from datetime import datetime


def datetime_to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp() * 1000000)


def timestamp_to_datetime(ts: int) -> datetime:
    return datetime.fromtimestamp(ts / 1e6)
