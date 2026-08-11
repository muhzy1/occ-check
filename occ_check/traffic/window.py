import os
import time
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional

def parse_time_window(last_str: Optional[str] = None, since_str: Optional[str] = None, until_str: Optional[str] = None) -> Tuple[float, float]:
    now = time.time()
    end_ts = now
    start_ts = now - 900

    if last_str:
        unit = last_str[-1].lower()
        val = int(last_str[:-1])
        if unit == 'm':
            start_ts = now - (val * 60)
        elif unit == 'h':
            start_ts = now - (val * 3600)
        elif unit == 'd':
            start_ts = now - (val * 86400)
    elif since_str:
        dt = datetime.strptime(since_str, "%Y-%m-%d %H:%M")
        start_ts = dt.timestamp()
        if until_str:
            dt_until = datetime.strptime(until_str, "%Y-%m-%d %H:%M")
            end_ts = dt_until.timestamp()

    return start_ts, end_ts

def binary_search_log_start(file_obj, start_ts: float, parse_timestamp_fn) -> int:
    file_obj.seek(0, os.SEEK_END)
    file_size = file_obj.tell()
    
    if file_size < 5 * 1024 * 1024:
        file_obj.seek(0)
        return 0

    low = 0
    high = file_size
    best_offset = 0

    while low <= high:
        mid = (low + high) // 2
        file_obj.seek(mid)
        file_obj.readline()
        
        offset = file_obj.tell()
        line = file_obj.readline()
        if not line:
            high = mid - 1
            continue

        ts = parse_timestamp_fn(line)
        if ts is None:
            low = mid + 1
            continue

        if ts >= start_ts:
            best_offset = offset
            high = mid - 1
        else:
            low = mid + 1

    file_obj.seek(best_offset)
    return best_offset
