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


if __name__ == "__main__":
    unittest.main()
