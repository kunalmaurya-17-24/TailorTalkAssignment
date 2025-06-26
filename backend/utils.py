from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def parse_natural_language_time(phrase: str) -> datetime:
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    phrase = phrase.lower()

    if "tomorrow afternoon" in phrase:
        return (now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)
    elif "tomorrow morning" in phrase:
        return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    elif "evening" in phrase:
        return now.replace(hour=18, minute=0, second=0, microsecond=0)
    elif "after lunch" in phrase:
        return now.replace(hour=14, minute=0, second=0, microsecond=0)

    return None
