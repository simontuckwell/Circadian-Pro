"""Card curve API: no live HA installation or network needed for tests."""

from __future__ import annotations

import ast
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest


PATH = Path(__file__).resolve().parents[1] / "custom_components/circadian_pro/card.py"


@dataclass(frozen=True)
class FakeSun:
    sunrise_time: object = "fixed"
    sunset_time: object = "fixed"
    min_sunrise_time: object = "early"
    max_sunrise_time: object = "late"
    min_sunset_time: object = "early"
    max_sunset_time: object = "late"
    sunrise_offset: timedelta = timedelta(minutes=20)
    sunset_offset: timedelta = timedelta(minutes=-20)


class CardCurveTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.package = ModuleType("cp_card_tests")
        self.package.__path__ = []
        self.frontend = ModuleType("cp_card_tests.frontend")

        def context(sun, now, zone, include_solar_elevation=False):
            self.calls.append((sun, now, zone, include_solar_elevation))
            return {
                "day_start": 0.0, "day_end": 86400.0,
                "generated_at": 43200.0, "timezone": zone,
                "sunrise": {"timestamp": 21600.0, "local_time": "06:00"},
                "sunset": {"timestamp": 64800.0, "local_time": "18:00"},
                "events": [{"event": "solar_noon", "timestamp": 43200.0}],
                "solar_elevation_samples": [[0, 0.0], [720, 1.0], [1440, 0.0]]
                    if include_solar_elevation else None,
            }

        self.frontend._solar_context = context
        sys.modules[self.package.__name__] = self.package
        sys.modules[self.frontend.__name__] = self.frontend
        tree = ast.parse(PATH.read_text(encoding="utf-8"))
        nodes = []
        for item in tree.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name in (
                "_card_curve", "websocket_card_curve"
            ):
                item.decorator_list = []
                nodes.append(item)
        self.ns = {
            "__name__": "cp_card_tests.card",
            "__package__": "cp_card_tests",
            "Any": object, "replace": replace, "timedelta": timedelta,
            "UTC": UTC, "datetime": datetime, "DOMAIN": "circadian_pro",
            "POLICY_READ": "read",
        }
        exec(compile(ast.fix_missing_locations(ast.Module(
            body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *nodes],
            type_ignores=[],
        )), str(PATH), "exec"), self.ns)
        self.settings = SimpleNamespace(
            brightness_mode="solar_elevation", sun=FakeSun(),
            min_brightness=10, max_brightness=50,
        )
        self.entity_id = "switch.circadian_pro_study"

    def tearDown(self):
        sys.modules.pop("cp_card_tests.frontend", None)
        sys.modules.pop("cp_card_tests", None)

    def test_actual_solar_mode_scales_progress_to_profile_limits(self):
        result = self.ns["_card_curve"](self.settings, datetime(2026, 11, 18, tzinfo=UTC), "Europe/London")
        self.assertEqual(result["points"], [[0.0, 10.0], [43200.0, 50.0], [86400.0, 10.0]])
        self.assertEqual(result["solar_noon"], 43200)
        self.assertEqual(result["sunrise"]["local_time"], "06:00")
        replaced_sun = self.calls[0][0]
        self.assertIsNone(replaced_sun.sunrise_time)
        self.assertIsNone(replaced_sun.sunset_time)
        self.assertEqual(replaced_sun.sunrise_offset, timedelta())
        self.assertEqual(self.settings.sun.sunrise_time, "fixed")
        self.assertEqual(self.calls[0][3], True)

    def test_other_modes_do_not_claim_to_show_a_solar_brightness_curve(self):
        self.settings.brightness_mode = "linear"
        result = self.ns["_card_curve"](self.settings, datetime.now(UTC), "Europe/London")
        self.assertEqual(result["mode"], "linear")
        self.assertEqual(result["points"], [])
        self.assertIs(self.calls[0][0], self.settings.sun)

    def test_access_check_precedes_read_or_profile_lookup(self):
        sent = []
        connection = SimpleNamespace(
            user=SimpleNamespace(permissions=SimpleNamespace(check_entity=lambda *args: False)),
            send_error=lambda *args: sent.append(args),
            send_result=lambda *args: self.fail("Must not return private data"),
        )
        hass = SimpleNamespace(data={"circadian_pro": {}}, config=SimpleNamespace(time_zone="Europe/London"))
        self._invoke(hass, connection)
        self.assertEqual(sent[0][1], "unauthorized")
        self.assertEqual(self.calls, [])

    def _invoke(self, hass, connection):
        coroutine = self.ns["websocket_card_curve"](hass, connection, {"id": 1, "entity_id": self.entity_id})
        try:
            coroutine.send(None)
        except StopIteration:
            return
        else:
            coroutine.close()
            self.fail("An unmocked asynchronous operation was attempted")

    def test_authorized_profile_returns_only_solar_data(self):
        results = []
        permissions = SimpleNamespace(check_entity=lambda entity, policy: policy == "read")
        connection = SimpleNamespace(
            user=SimpleNamespace(permissions=permissions),
            send_error=lambda *args: self.fail(str(args)),
            send_result=lambda *args: results.append(args),
        )
        switch = SimpleNamespace(
            entity_id=self.entity_id, _sun_light_settings=self.settings,
            sleep_mode_switch=SimpleNamespace(entity_id="switch.study_sleep"),
        )
        async def executor(fn, *args):
            return fn(*args)
        hass = SimpleNamespace(
            data={"circadian_pro": {"loaded": {"switch": switch}, "manager": object()}},
            config=SimpleNamespace(time_zone="Europe/London"),
            async_add_executor_job=executor,
        )
        self._invoke(hass, connection)
        payload = results[0][1]
        self.assertEqual(payload["sleep_entity_id"], "switch.study_sleep")
        self.assertEqual(payload["points"][1][1], 50)
        self.assertNotIn("configuration", payload)
        self.assertEqual(len(self.calls), 1)


if __name__ == "__main__":
    unittest.main()
