"""Solar Elevation mode: actual sun height, CL normalisation, and safety limits."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import sys
import unittest

import test_audit_lighting as lighting_fixtures


class SolarHeightAstral(lighting_fixtures.FixedAstral):
    """Simple deterministic height curve: 0 at 06/18, 60 degrees at noon."""

    def solar_elevation(self, when):
        time = when.astimezone(UTC)
        hours = time.hour + time.minute / 60 + time.second / 3600
        if hours <= 6 or hours >= 18:
            return 0 if hours in (6, 18) else -5
        return 60 * (1 - abs(hours - 12) / 6)


class SolarElevationTests(unittest.TestCase):
    def setUp(self):
        self.color = lighting_fixtures.load_module("color_and_brightness.py")
        self.day = datetime(2026, 10, 14, tzinfo=UTC)

    def tearDown(self):
        sys.modules.pop(self.color.__name__, None)

    def settings(self, **overrides):
        data = dict(
            name="Solar elevation", astral_location=SolarHeightAstral(),
            adapt_until_sleep=False, max_brightness=50, min_brightness=10,
            max_color_temp=6000, min_color_temp=2000, sleep_brightness=3,
            sleep_rgb_or_color_temp="color_temp", sleep_color_temp=1800,
            sleep_rgb_color=(255, 56, 0),
            sunrise_time=None, min_sunrise_time=None, max_sunrise_time=None,
            sunset_time=None, min_sunset_time=None, max_sunset_time=None,
            brightness_mode="solar_elevation", brightness_mode_time_dark=timedelta(hours=3),
            brightness_mode_time_light=timedelta(minutes=1),
        )
        data.update(overrides)
        return self.color.SunLightSettings(**data)

    def brightness(self, settings, hour, sleeping=False):
        return settings.brightness_and_color(self.day + timedelta(hours=hour), sleeping)["brightness_pct"]

    def test_minimum_at_night_and_horizon_maximum_at_solar_noon(self):
        settings = self.settings()
        for hour in (0, 6, 18, 23):
            self.assertEqual(self.brightness(settings, hour), 10)
        self.assertEqual(self.brightness(settings, 12), 50)
        nine = self.brightness(settings, 9)
        fifteen = self.brightness(settings, 15)
        self.assertAlmostEqual(nine, fifteen)
        self.assertAlmostEqual(nine, 10 + 40 * (30 + 0.833) / (60 + 0.833))
        self.assertTrue(10 < nine < 50)

    def test_real_sun_height_not_sunrise_sunset_windows(self):
        settings = self.settings(
            sunrise_offset=timedelta(minutes=40),
            sunset_offset=timedelta(minutes=-40),
            brightness_mode_time_dark=timedelta(hours=4),
            brightness_mode_time_light=timedelta(hours=4),
        )
        self.assertEqual(self.brightness(settings, 12), 50)
        self.assertAlmostEqual(self.brightness(settings, 9), self.brightness(self.settings(), 9))
        self.assertTrue(10 < self.brightness(settings, 15) < 50)

    def test_colour_temperature_keeps_independent_curve(self):
        settings = self.settings(apply_temperature_curve=True)
        result = settings.brightness_and_color(self.day + timedelta(hours=9), False)
        self.assertAlmostEqual(result["brightness_pct"], 10 + 40 * (30 + 0.833) / (60 + 0.833))
        self.assertEqual(result["color_temp_kelvin"], settings.color_temp_kelvin(result["sun_position"]))

    def test_explicit_sleep_mode_takes_priority(self):
        settings = self.settings()
        result = settings.brightness_and_color(self.day + timedelta(hours=12), True)
        self.assertEqual(result["brightness_pct"], 3)
        self.assertEqual(result["color_temp_kelvin"], 1800)

    def test_equal_brightness_limits_and_bounded_progress(self):
        fixed = self.settings(min_brightness=25, max_brightness=25)
        for hour in (0, 6, 9, 12, 15, 18, 23):
            self.assertEqual(self.brightness(fixed, hour), 25)
        sun = self.settings().sun
        for hour in (0, 6, 9, 12, 15, 18, 23):
            value = sun.solar_elevation_progress(self.day + timedelta(hours=hour))
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 1)


if __name__ == "__main__":
    unittest.main()
