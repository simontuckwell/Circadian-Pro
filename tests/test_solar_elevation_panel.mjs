/** Solar Elevation preview consumes the engine's Astral samples, not a time approximation. */

import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const source = await readFile(new URL("../custom_components/circadian_pro/frontend/calibration-panel.js", import.meta.url), "utf8");
const previousHTMLElement = globalThis.HTMLElement;
const previousCustomElements = globalThis.customElements;
globalThis.HTMLElement = class {};
globalThis.customElements = { get: () => undefined, define: () => {} };
const { brightnessTimingPoints, brightnessTimingValue, solarDraft } =
  await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`);
if (previousHTMLElement === undefined) delete globalThis.HTMLElement;
else globalThis.HTMLElement = previousHTMLElement;
if (previousCustomElements === undefined) delete globalThis.customElements;
else globalThis.customElements = previousCustomElements;

const hour = 3600;
const samples = [[0, 0], [360, 0], [540, .5], [720, 1], [900, .5], [1080, 0], [1440, 0]];
const context = {
  timezone: "Europe/London", local_date: "2026-10-14",
  day_start: 0, day_end: 24 * hour, refresh_after: 24 * hour,
  sunrise: { timestamp: 6 * hour, local_time: "06:00" },
  sunset: { timestamp: 18 * hour, local_time: "18:00" },
  events: [
    { event: "solar_midnight", timestamp: -12 * hour },
    { event: "sunrise", timestamp: 6 * hour },
    { event: "solar_noon", timestamp: 12 * hour },
    { event: "sunset", timestamp: 18 * hour },
    { event: "solar_midnight", timestamp: 24 * hour },
    { event: "sunrise", timestamp: 30 * hour },
  ],
  solar_elevation_samples: samples,
};

test("Solar Elevation preview uses server-generated progress samples", () => {
  assert.deepEqual(brightnessTimingPoints("solar_elevation", undefined, undefined, context), samples);
  assert.equal(brightnessTimingValue(720, "solar_elevation", 1, 60, context), 1);
  assert.equal(brightnessTimingValue(630, "solar_elevation", 1, 60, context), .75);
  assert.equal(brightnessTimingValue(60, "solar_elevation", 1, 60, context), 0);
});

test("Solar Elevation refuses a preview without physical solar samples", () => {
  const missing = { ...context, solar_elevation_samples: null };
  assert.equal(brightnessTimingPoints("solar_elevation", 1, 60, missing), null);
  assert.ok(Number.isNaN(brightnessTimingValue(720, "solar_elevation", 1, 60, missing)));
});

test("Mode changes refresh the server solar context without reacting to brightness sliders", () => {
  const natural = solarDraft({ brightness_mode: "default", min_brightness: 10, sunrise_offset_minutes: 0 });
  const solar = solarDraft({ brightness_mode: "solar_elevation", min_brightness: 40, sunrise_offset_minutes: 0 });
  assert.notDeepEqual(natural, solar);
  assert.equal(solar.brightness_mode, "solar_elevation");
  assert.equal(solar.min_brightness, undefined);
  assert.equal(solar.sunrise_offset_minutes, 0);
});
