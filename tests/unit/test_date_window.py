from __future__ import annotations

import importlib.util
import unittest
from datetime import date
from pathlib import Path


def load_date_window_module():
    module_path = (
        Path(__file__).resolve().parents[2]
        / "custom_components"
        / "aula_easyiq"
        / "date_window.py"
    )
    spec = importlib.util.spec_from_file_location("easyiq_date_window", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


date_window = load_date_window_module()


class BusinessTargetDatesTests(unittest.TestCase):
    def test_wednesday_keeps_monday_and_tuesday(self) -> None:
        # 2026-11-11 is a Wednesday
        self.assertEqual(
            date_window.business_target_dates(date(2026, 11, 11), 5),
            [
                date(2026, 11, 9),
                date(2026, 11, 10),
                date(2026, 11, 11),
                date(2026, 11, 12),
                date(2026, 11, 13),
                date(2026, 11, 16),
                date(2026, 11, 17),
            ],
        )

    def test_monday_adds_no_earlier_days(self) -> None:
        self.assertEqual(
            date_window.business_target_dates(date(2026, 11, 9), 2),
            [date(2026, 11, 9), date(2026, 11, 10)],
        )

    def test_weekend_keeps_the_past_week_and_skips_to_monday(self) -> None:
        # 2026-11-14 is a Saturday
        self.assertEqual(
            date_window.business_target_dates(date(2026, 11, 14), 1),
            [
                date(2026, 11, 9),
                date(2026, 11, 10),
                date(2026, 11, 11),
                date(2026, 11, 12),
                date(2026, 11, 13),
                date(2026, 11, 16),
            ],
        )

    def test_zero_days_returns_nothing(self) -> None:
        self.assertEqual(date_window.business_target_dates(date(2026, 11, 11), 0), [])

    def test_sunday_keeps_the_past_week(self) -> None:
        # 2026-11-15 is a Sunday
        self.assertEqual(
            date_window.business_target_dates(date(2026, 11, 15), 1),
            [date(2026, 11, d) for d in (9, 10, 11, 12, 13, 16)],
        )

    def test_friday_keeps_four_earlier_days(self) -> None:
        # 2026-11-13 is a Friday
        self.assertEqual(
            date_window.business_target_dates(date(2026, 11, 13), 1),
            [date(2026, 11, d) for d in (9, 10, 11, 12, 13)],
        )

    def test_forward_window_spans_two_weekends(self) -> None:
        # Thursday 2026-11-12 with 7 business days forward
        dates = date_window.business_target_dates(date(2026, 11, 12), 7)
        self.assertEqual(dates[:3], [date(2026, 11, 9), date(2026, 11, 10), date(2026, 11, 11)])
        self.assertEqual(
            dates[3:],
            [date(2026, 11, d) for d in (12, 13, 16, 17, 18, 19, 20)],
        )

    def test_negative_days_returns_nothing(self) -> None:
        self.assertEqual(date_window.business_target_dates(date(2026, 11, 11), -1), [])

    def test_without_earlier_weekdays_starts_today(self) -> None:
        self.assertEqual(
            date_window.business_target_dates(
                date(2026, 11, 11), 2, include_earlier_weekdays=False
            ),
            [date(2026, 11, 11), date(2026, 11, 12)],
        )


if __name__ == "__main__":
    unittest.main()
