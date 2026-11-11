"""Pure date helpers for choosing which school days to keep."""

from __future__ import annotations

import datetime


def business_target_dates(
    today: datetime.date, days: int, include_earlier_weekdays: bool = True
) -> list[datetime.date]:
    """Return the weekdays to keep: earlier days of this week, then N business days from today.

    Earlier weekdays of the current week are kept so a weekly schedule does not
    lose Monday and Tuesday by Wednesday. Pass include_earlier_weekdays=False
    to get only the N business days from today (e.g. for homework).
    """
    if days <= 0:
        return []

    start_of_week = today - datetime.timedelta(days=today.weekday())
    earlier = min(today.weekday(), 5) if include_earlier_weekdays else 0
    dates = [start_of_week + datetime.timedelta(days=i) for i in range(earlier)]

    check_date = today
    found = 0
    while found < days:
        if check_date.weekday() < 5:
            dates.append(check_date)
            found += 1
        check_date += datetime.timedelta(days=1)
    return dates
