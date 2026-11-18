/** Circadian Pro card: pure graph/state helpers and UI actions, without a browser. */
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const source = await readFile(
  new URL("../custom_components/circadian_pro/frontend/circadian-pro-card.js", import.meta.url),
  "utf8",
);
const previous = { HTMLElement: globalThis.HTMLElement, customElements: globalThis.customElements };
globalThis.HTMLElement = class {
  attachShadow() {
    this.shadowRoot = { innerHTML: "", querySelector: () => null };
  }
};
const registry = new Map();
globalThis.customElements = {
  get: (key) => registry.get(key),
  define: (key, value) => registry.set(key, value),
};
const { profileStatus, curveGeometry, interpolatePoints, escapeHtml, CircadianProCard } =
  await import("data:text/javascript;base64," + Buffer.from(source).toString("base64"));
for (const [name, value] of Object.entries(previous)) {
  if (value === undefined) delete globalThis[name];
  else globalThis[name] = value;
}

const points = [[0, 10], [21600, 10], [43200, 50], [64800, 10], [86400, 10]];
const curve = { day_start: 0, day_end: 86400, min_brightness: 10, max_brightness: 50, points };

test("automatic, manual, paused and unavailable states are distinct", () => {
  assert.equal(profileStatus("on", { manual_control: [] }), "Automatic");
  assert.equal(profileStatus("on", { manual_control: ["light.study"] }), "Manual");
  assert.equal(profileStatus("off", { manual_control: ["light.study"] }), "Paused");
  assert.equal(profileStatus("unavailable"), "Unavailable");
});

test("actual solar samples control path geometry and live marker", () => {
  assert.equal(interpolatePoints(points, 32400), 30);
  assert.equal(interpolatePoints(points, -200), 10);
  assert.equal(interpolatePoints(points, 90000), 10);
  const graph = curveGeometry(curve, 43200);
  assert.ok(graph.path.startsWith("M19.00 79.00"));
  assert.equal(graph.nowY, 12);
  assert.equal(curveGeometry({ ...curve, points: [[0, 10], [0, 20]] }, 43200), null);
});

test("room titles are safely escaped", () => {
  assert.equal(escapeHtml("<script>&"), "&lt;script&gt;&amp;");
  const card = new CircadianProCard();
  card.setConfig({ entity: "switch.circadian_pro_study", name: "<b>Study</b>" });
  card.hass = { states: {
    "switch.circadian_pro_study": {
      state: "on", attributes: { brightness_pct: 32, color_temp_kelvin: 3200, manual_control: [] },
    },
  } };
  assert.match(card.shadowRoot.innerHTML, /&lt;b&gt;Study&lt;\/b&gt;/);
  assert.match(card.shadowRoot.innerHTML, /Automatic/);
});

test("small toggle and manual resume use existing, scoped HA services", async () => {
  const card = new CircadianProCard();
  const id = "switch.circadian_pro_study";
  card.setConfig({ entity: id });
  const calls = [];
  card.hass = { states: { [id]: { state: "on", attributes: { manual_control: ["light.study"] } } },
    callService: async (...args) => calls.push(args) };
  await card._resume();
  await card._toggle();
  assert.deepEqual(calls, [
    ["circadian_pro", "set_manual_control", { entity_id: id, manual_control: "false" }],
    ["switch", "turn_off", { entity_id: id }],
  ]);
});

test("paused profiles can still display their last known calculated targets", () => {
  const card = new CircadianProCard();
  const id = "switch.circadian_pro_study";
  card.setConfig({ entity: id });
  card.hass = { states: { [id]: {
    state: "off",
    attributes: { last_target_brightness_pct: 43, last_target_color_temp_kelvin: 3600 },
  } } };
  assert.match(card.shadowRoot.innerHTML, /43/);
  assert.match(card.shadowRoot.innerHTML, /3,600/);
  assert.match(card.shadowRoot.innerHTML, /Paused/);
});
