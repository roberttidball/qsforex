from __future__ import print_function

import json
from datetime import date, timedelta

try:
    from urllib.parse import urlencode
    from urllib.request import urlopen
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen


BASE_URL = "https://api.fxmacrodata.com/v1/calendar/{currency}"


def fetch_calendar(currency="USD", start_date=None, end_date=None, timeout=20):
    today = date.today()
    start_date = start_date or today.isoformat()
    end_date = end_date or (today + timedelta(days=14)).isoformat()
    query = urlencode({"start_date": start_date, "end_date": end_date})

    with urlopen("{}?{}".format(BASE_URL.format(currency=currency), query), timeout=timeout) as response:
        payload = json.load(response)

    events = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(events, list):
        detail = payload.get("detail") if isinstance(payload, dict) else None
        raise ValueError("FXMacroData returned an unexpected response: {}".format(detail or "missing data list"))
    return [event for event in events if isinstance(event, dict)]


def top_tier_blackout_dates(events):
    dates = set()
    for event in events:
        if event.get("top_tier_for_currency") or event.get("market_tier") == 1:
            event_time = event.get("announcement_datetime_utc") or event.get("announcement_datetime_local")
            dates.add((event_time or event.get("date", ""))[:10])
    return sorted(item for item in dates if item)


if __name__ == "__main__":
    events = fetch_calendar(start_date="2026-07-01", end_date="2026-07-20")
    print("Avoid opening new FX risk on these top-tier USD macro dates:")
    for event_date in top_tier_blackout_dates(events):
        print("  - {}".format(event_date))
