"""Read-only daily curve for Circadian Pro dashboard cards.

Dashboard data is deliberately narrower than the administrator calibration API.
The caller must be allowed to read the profile switch; neither settings nor
lights can be modified by this endpoint.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any

try:
    import probatio as ws_schema
except ImportError:
    import voluptuous as ws_schema

from homeassistant.auth.permissions.const import POLICY_READ
from homeassistant.components import websocket_api

from .const import DOMAIN


def _card_curve(settings: Any, now: datetime, timezone_name: str) -> dict[str, Any]:
    """Sample the exact engine curve outside the HA event loop."""
    from .frontend import _solar_context

    mode = settings.brightness_mode
    # Solar Elevation intentionally ignores configured or fixed sunrise/sunset
    # times. Display real astronomical event labels for that mode too.
    sun = settings.sun
    if mode == "solar_elevation":
        sun = replace(
            sun,
            sunrise_time=None, sunset_time=None,
            min_sunrise_time=None, max_sunrise_time=None,
            min_sunset_time=None, max_sunset_time=None,
            sunrise_offset=timedelta(), sunset_offset=timedelta(),
        )
    context = _solar_context(
        sun, now, timezone_name, include_solar_elevation=mode == "solar_elevation",
    )
    noon = next(
        (event["timestamp"] for event in context["events"]
         if event["event"] == "solar_noon"
         and context["day_start"] <= event["timestamp"] < context["day_end"]),
        None,
    )
    progress = context["solar_elevation_samples"] or []
    low, high = settings.min_brightness, settings.max_brightness
    return {
        "day_start": context["day_start"],
        "day_end": context["day_end"],
        "generated_at": context["generated_at"],
        "timezone": context["timezone"],
        "mode": mode,
        "min_brightness": low,
        "max_brightness": high,
        "sunrise": context["sunrise"],
        "sunset": context["sunset"],
        "solar_noon": noon,
        "points": [
            [round(context["day_start"] + minutes * 60, 3),
             round(low + (high - low) * fraction, 3)]
            for minutes, fraction in progress
        ],
    }


@websocket_api.websocket_command({
    "type": "circadian_pro/card/curve",
    ws_schema.Required("entity_id"): str,
})
@websocket_api.async_response
async def websocket_card_curve(hass: Any, connection: Any, msg: dict[str, Any]) -> None:
    """Return only the curve of a CP profile the current user may read."""
    entity_id = msg["entity_id"]
    if not connection.user.permissions.check_entity(entity_id, POLICY_READ):
        connection.send_error(msg["id"], "unauthorized", "You cannot read this profile.")
        return

    switch = next(
        (entry.get("switch") for entry in hass.data.get(DOMAIN, {}).values()
         if isinstance(entry, dict)
         and getattr(entry.get("switch"), "entity_id", None) == entity_id),
        None,
    )
    if switch is None:
        connection.send_error(msg["id"], "not_found", "Circadian Pro profile is not loaded.")
        return

    try:
        result = await hass.async_add_executor_job(
            _card_curve, switch._sun_light_settings, datetime.now(UTC),
            hass.config.time_zone,
        )
    except (ValueError, OverflowError) as err:
        connection.send_error(msg["id"], "solar_unavailable", str(err))
        return

    sleep_entity = getattr(getattr(switch, "sleep_mode_switch", None), "entity_id", None)
    result["sleep_entity_id"] = (
        sleep_entity if sleep_entity
        and connection.user.permissions.check_entity(sleep_entity, POLICY_READ) else None
    )
    connection.send_result(msg["id"], result)
