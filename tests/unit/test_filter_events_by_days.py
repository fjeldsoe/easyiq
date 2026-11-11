from __future__ import annotations

import datetime
import importlib.util
import sys
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INTEGRATION_DIR = ROOT / "custom_components" / "aula_easyiq"
if str(INTEGRATION_DIR) in sys.path:
    sys.path.remove(str(INTEGRATION_DIR))
import calendar as _stdlib_calendar  # noqa: E402,F401 - keep stdlib calendar loaded


def load_module(name: str, filename: str):
    sys.path.insert(0, str(INTEGRATION_DIR))
    spec = importlib.util.spec_from_file_location(name, INTEGRATION_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


mitid_auth = load_module("mitid_auth", "mitid_auth.py")
client_module = load_module("easyiq_client_filter_test", "client.py")


def _event(day: datetime.date) -> dict[str, str]:
    return {"start": f"{day.isoformat()}T08:00:00", "courses": "Dansk"}


class FilterEventsByDaysTests(unittest.TestCase):
    def setUp(self) -> None:
        token_state = mitid_auth.AulaTokenState(
            access_token="access-123",
            refresh_token="refresh-123",
            expires_at=time.time() + 3600,
        )
        self.client = client_module.EasyIQClient("guardian@example.test", token_state)
        self.today = datetime.datetime.now().date()
        self.monday = self.today - datetime.timedelta(days=self.today.weekday())

    def test_weekplan_keeps_monday_of_this_week(self) -> None:
        events = [_event(self.monday), _event(self.today)]
        kept = self.client._filter_events_by_days(events, 5)
        self.assertIn(_event(self.monday), kept)

    def test_homework_drops_earlier_weekdays(self) -> None:
        if self.today == self.monday:
            self.skipTest("no earlier weekday when today is Monday")
        events = [_event(self.monday), _event(self.today)]
        kept = self.client._filter_events_by_days(
            events, 5, include_earlier_weekdays=False
        )
        self.assertNotIn(_event(self.monday), kept)

    def test_upcoming_events_drops_past_days(self) -> None:
        if self.today == self.monday:
            self.skipTest("no earlier weekday when today is Monday")
        events = [_event(self.monday), _event(self.today)]
        self.assertEqual(client_module._upcoming_events(events), [_event(self.today)])
        slash = {"start": self.monday.strftime("%Y/%m/%d") + " 08:00"}
        self.assertEqual(client_module._upcoming_events([slash]), [])


if __name__ == "__main__":
    unittest.main()
