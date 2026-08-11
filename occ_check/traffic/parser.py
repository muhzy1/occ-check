import re
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

LOG_REGEX = re.compile(
    r'^(?P\S+)\s+\S+\s+\S+\s+\[(?P[^\]]+)\]\s+"(?PGET|POST|HEAD|PUT|DELETE|OPTIONS|CONNECT|PATCH)?\s*(?P\S+)?\s*(?:HTTP/\d\.\d)?"\s+(?P\d{3})\s+(?P\S+)\s*"(?P[^"]*)"\s*"(?P[^"]*)"'
)

MONTH_MAP = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

def parse_apache_timestamp(time_str: str) -> Optional[float]:
    try:
        parts = time_str.split()
        dt_part = parts[0]
        tz_part = parts[1] if len(parts) > 1 else "+0000"

        day_str, month_str, rest = dt_part.split('/', 2)
        year_str, hour_str, min_str, sec_str = rest.split(':')

        day = int(day_str)
        month = MONTH_MAP[month_str]
        year = int(year_str)
        hour = int(hour_str)
        minute = int(min_str)
        second = int(sec_str)

        tz_sign = 1 if tz_part[0] == '+' else -1
        tz_hours = int(tz_part[1:3])
        tz_mins = int(tz_part[3:5])
        tz_delta = timedelta(hours=tz_hours, minutes=tz_mins) * tz_sign

        tz = timezone(tz_delta)
        dt = datetime(year, month, day, hour, minute, second, tzinfo=tz)
        return dt.timestamp()
    except Exception:
        return None

def parse_line(line: str) -> Optional[Dict[str, Any]]:
    match = LOG_REGEX.match(line)
    if not match:
        return None
    
    data = match.groupdict()
    ts = parse_apache_timestamp(data['time'])
    if ts is None:
        return None

    data['timestamp'] = ts
    return data
