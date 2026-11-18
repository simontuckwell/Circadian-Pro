"""Regression scenarios for the switch/manager audit, using production methods."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from types import MethodType, SimpleNamespace
import unittest

from test_color_temperature_bounds import (
    ProtocolHarness, State, complete_immediate, load_functions, production_namespace,
)
from test_entity_translations import ServiceValidationError


def namespace():
    ns = production_namespace()
    ns.update(
        asyncio=asyncio, STATE_ON="on", STATE_OFF="off",
        STATE_UNKNOWN="unknown", STATE_UNAVAILABLE="unavailable",
        CONF_PARAMS="params", CONF_LIGHTS="lights", _DOMAIN_SHORT="cp",
        SERVICE_TURN_OFF="turn_off", SERVICE_TOGGLE="toggle", Mapping=Mapping,
        is_on=lambda hass, light: (state := hass.states.get(light)) is not None and state.state == "on",
        is_calibration_preview_context=lambda *_: False,
        ServiceValidationError=ServiceValidationError,
    )
    load_functions(ns, "helpers.py", {"remove_vowels"})
    load_functions(ns, "switch.py", {
        "is_our_context", "is_our_context_id", "_expand_light_groups", "_is_light_group",
        "NoSwitchFoundError", "_switches_with_lights", "_switches_from_service_call",
        "MAX_STATE_HISTORY", "_service_parameters",
    })
    return ns


class GroupExpansionTests(unittest.TestCase):
    def test_nested_groups_expand_to_unique_physical_lights(self):
        ns = namespace()
        states = {
            "light.room": State({"entity_id": ["light.nested", "light.a"]}),
            "light.nested": State({"entity_id": ["light.a", "light.b"]}),
            "light.a": State({}), "light.b": State({}),
        }
        hass = SimpleNamespace(states=SimpleNamespace(get=states.get))
        self.assertEqual(ns["_expand_light_groups"](hass, ["light.room"]), ["light.a", "light.b"])

    def test_cycle_does_not_loop_or_hide_other_members(self):
        ns = namespace()
        states = {
            "light.room": State({"entity_id": ["light.nested", "light.a"]}),
            "light.nested": State({"entity_id": ["light.room", "light.b"]}),
            "light.a": State({}), "light.b": State({}),
        }
        hass = SimpleNamespace(states=SimpleNamespace(get=states.get))
        self.assertEqual(ns["_expand_light_groups"](hass, ["light.room"]), ["light.a", "light.b"])

    def test_hue_group_stays_a_single_hardware_target(self):
        ns = namespace()
        state = State({"entity_id": ["light.a"], "is_hue_group": True})
        hass = SimpleNamespace(states=SimpleNamespace(get=lambda _: state))
        self.assertEqual(ns["_expand_light_groups"](hass, ["light.hue"]), ["light.hue"])


class AdaptationSafetyTests(unittest.TestCase):
    def test_redundant_initial_target_still_detects_first_hue_app_override(self):
        """An already-correct Hue room must not need a second manual adjustment."""
        h = ProtocolHarness(modes=("color_temp",))
        h.switch._skip_redundant_commands = True
        # The initial brightness and CT already equal CP's requested targets.
        payload = h.dispatch(3500)
        self.assertIsNone(payload)
        self.assertEqual(h.calls, [])
        self.assertEqual(h.manager.last_service_data[h.light]["brightness"], 255)
        self.assertEqual(h.manager.last_service_data[h.light]["color_temp_kelvin"], 3500)

        # Change the room via Hue, not a HA light.turn_on service call.
        h.state.attributes["brightness"] = 95
        changed = complete_immediate(h.ns["significant_change"](
            h.manager, h.switch, h.light, SimpleNamespace(id="poll"),
        ))
        self.assertIn(h.ns["LightControlAttributes"].BRIGHTNESS, changed)
        complete_immediate(h.ns["update_manually_controlled_from_untracked_change"](
            h.manager, h.switch, h.light, False, SimpleNamespace(id="poll"),
        ))
        self.assertTrue(h.manager.manual_control[h.light].has_any())
        self.assertTrue(h.events)

    def test_partial_redundant_target_retains_unsent_brightness_baseline(self):
        h = ProtocolHarness(modes=("color_temp",))
        h.switch._skip_redundant_commands = True
        # A needed colour command is sent, but the brightness command is omitted.
        h.dispatch(4000)
        self.assertEqual(len(h.calls), 1)
        self.assertEqual(h.manager.last_service_data[h.light]["brightness"], 255)
        self.assertEqual(h.manager.last_service_data[h.light]["color_temp_kelvin"], 4000)
        h.state.attributes["brightness"] = 100
        changed = complete_immediate(h.ns["significant_change"](
            h.manager, h.switch, h.light, SimpleNamespace(id="poll"),
        ))
        self.assertIn(h.ns["LightControlAttributes"].BRIGHTNESS, changed)

    def test_nonredundant_targets_are_not_assumed_to_have_been_applied(self):
        h = ProtocolHarness(modes=("color_temp",))
        h.switch._skip_redundant_commands = True
        h.dispatch(4000)
        # A colour command was sent and its expected value is known; the
        # unsent baseline is seeded only from attributes matching HA state.
        self.assertEqual(h.manager.last_service_data[h.light]["brightness"], 255)
        self.assertEqual(h.manager.last_service_data[h.light]["color_temp_kelvin"], 4000)

    def test_split_commands_keep_brightness_for_external_change_detection(self):
        h = ProtocolHarness()
        h.switch._separate_turn_on_commands = True
        payload = h.dispatch(3500)
        h.state.attributes.update(color_mode="rgbww", rgbww_color=payload["rgbww_color"], brightness=1)
        changed = complete_immediate(h.ns["significant_change"](h.manager, h.switch, h.light, SimpleNamespace(id="poll")))
        self.assertIn(h.ns["LightControlAttributes"].BRIGHTNESS, changed)
        self.assertNotIn(h.ns["LightControlAttributes"].COLOR, changed)

    def test_overlapping_update_does_not_mutate_the_prior_batch_snapshot(self):
        h = ProtocolHarness()
        h.switch._sun_light_settings = SimpleNamespace(sleep_rgb_or_color_temp="color_temp")
        snapshot = {"brightness_pct": 80, "color_temp_kelvin": 4000}
        complete_immediate(h.ns["prepare_switch_adaptation_data"](
            h.switch, h.light, settings=snapshot, effective_sleep=False, force=True,
        ))
        # Another callback publishes newer settings while the first batch
        # awaits a refresh; its remaining lights still use their original sample.
        h.switch._settings.update(brightness_pct=10, color_temp_kelvin=1200)
        data = complete_immediate(h.ns["prepare_switch_adaptation_data"](
            h.switch, "light.next", settings=snapshot, effective_sleep=False, force=True,
        ))
        payload = complete_immediate(data.next_service_call_data())
        self.assertEqual(snapshot["brightness_pct"], 80)
        self.assertEqual(payload["brightness"], 204)

    def test_deleted_light_does_not_raise_or_send_a_command(self):
        h = ProtocolHarness()
        h.state = None
        h.switch._sun_light_settings = SimpleNamespace(get_settings=lambda *_: {"brightness_pct": 50})
        data = complete_immediate(h.ns["prepare_switch_adaptation_data"](h.switch, h.light, force=True))
        self.assertIsNone(data)
        self.assertEqual(h.calls, [])

    def test_white_only_light_uses_kelvin_in_rgb_sleep_mode(self):
        h = ProtocolHarness(modes=("color_temp",))
        payload = h.dispatch(1000, sleep=True)
        self.assertNotIn("rgb_color", payload)
        self.assertEqual(payload["color_temp_kelvin"], 2000)

    def test_native_ct_preference_is_honored_for_dual_mode_rgb_light(self):
        h = ProtocolHarness(modes=("color_temp", "rgb"))
        payload = h.dispatch(4000)
        self.assertEqual(payload.get("color_temp_kelvin"), 4000)
        self.assertNotIn("rgb_color", payload)
        h.switch._prefer_rgb_color = True
        payload = h.dispatch(4000)
        self.assertIn("rgb_color", payload)
        self.assertNotIn("color_temp_kelvin", payload)

    def test_rgb_still_produces_targets_below_native_ct_range(self):
        h = ProtocolHarness(modes=("color_temp", "rgb"))
        payload = h.dispatch(1200)
        self.assertIn("rgb_color", payload)
        self.assertNotIn("color_temp_kelvin", payload)


class ManagerEventTests(unittest.IsolatedAsyncioTestCase):
    async def test_manual_takeover_while_split_waits_stops_remaining_color_command(self):
        h = ProtocolHarness()
        h.switch._separate_turn_on_commands = True
        async def manual_during_wait(_):
            h.manager.manual_control[h.light] = h.ns["LightControlAttributes"].COLOR
        h.ns["asyncio"] = SimpleNamespace(sleep=manual_during_wait)
        h.dispatch(3500)
        self.assertEqual(len(h.calls), 1)
        self.assertIn("brightness", h.calls[0][2])
        self.assertNotIn("rgbww_color", h.calls[0][2])

    async def test_mixed_service_target_only_tracks_managed_lights(self):
        ns = namespace()
        load_functions(ns, "switch.py", {"turn_on_off_event_listener"}, "CircadianProManager")
        reset = []
        manager = SimpleNamespace(
            hass=SimpleNamespace(), lights={"light.owned"},
            turn_off_event={}, reset=lambda *lights: reset.extend(lights),
            _get_entity_list=lambda _: ["light.owned", "light.unrelated"],
        )
        event = SimpleNamespace(data={"domain": "light", "service": "turn_off", "service_data": {}}, context=SimpleNamespace(id="external"))
        await ns["turn_on_off_event_listener"](manager, event)
        self.assertEqual(reset, ["light.owned"])
        self.assertEqual(set(manager.turn_off_event), {"light.owned"})

    async def test_manual_updates_do_not_accumulate_in_own_report_history(self):
        ns = namespace()
        load_functions(ns, "switch.py", {"state_changed_event_listener"}, "CircadianProManager")
        own = State({}, context_id="0000000000:cp:AAAA:intr:00")
        own.state = "on"
        external = State({}, context_id="external")
        external.state = "on"
        manager = SimpleNamespace(hass=SimpleNamespace(), lights={"light.a"}, our_last_state_on_change={"light.a": [own]}, is_proactively_adapting=lambda *_: False)
        event = SimpleNamespace(data={"entity_id": "light.a", "old_state": external, "new_state": external}, context=external.context)
        for _ in range(500):
            await ns["state_changed_event_listener"](manager, event)
        self.assertEqual(manager.our_last_state_on_change["light.a"], [own])

    async def test_own_transition_history_is_bounded_and_keeps_latest_ack(self):
        ns = namespace()
        load_functions(ns, "switch.py", {"state_changed_event_listener"}, "CircadianProManager")
        reports = []
        manager = SimpleNamespace(hass=SimpleNamespace(), lights={"light.a"}, our_last_state_on_change={}, start_transition_timer=lambda _: None, is_proactively_adapting=lambda *_: False)
        for index in range(200):
            state = State({"brightness": index}, context_id="0000000000:cp:AAAA:intr:00")
            reports.append(state)
            event = SimpleNamespace(data={"entity_id": "light.a", "old_state": state, "new_state": state}, context=state.context)
            await ns["state_changed_event_listener"](manager, event)
        history = manager.our_last_state_on_change["light.a"]
        self.assertLessEqual(len(history), 8)
        self.assertIs(history[0], reports[0])
        self.assertIs(history[-1], reports[-1])

    async def test_preview_reservation_blocks_a_pending_normal_command(self):
        h = ProtocolHarness()
        h.ns["is_calibration_preview_active"] = lambda *_: True
        h.ns["is_our_context"] = namespace()["is_our_context"]
        async def next_payload():
            return {"entity_id": h.light, "brightness": 100}
        data = SimpleNamespace(entity_id=h.light, context=SimpleNamespace(id="interval"), max_length=1, initial_sleep=False, force=True, next_service_call_data=next_payload)
        await h.ns["_execute_adaptation_calls"](h.switch, data)
        self.assertEqual(h.calls, [])

    async def test_calibration_can_control_an_off_profile_reserved_for_preview(self):
        h = ProtocolHarness()
        h.switch.is_on = False
        h.ns["is_calibration_preview_active"] = lambda *_: True
        h.ns["is_our_context"] = namespace()["is_our_context"]
        async def next_payload():
            return {"entity_id": h.light, "brightness": 100}
        data = SimpleNamespace(entity_id=h.light, context=SimpleNamespace(id="0000000000:cp:AAAA:clbr:00"), max_length=1, initial_sleep=False, force=True, next_service_call_data=next_payload)
        await h.ns["_execute_adaptation_calls"](h.switch, data)
        self.assertEqual(len(h.calls), 1)

    async def test_explicit_apply_is_allowed_when_profile_off(self):
        h = ProtocolHarness()
        h.switch.is_on = False
        h.ns["is_our_context"] = namespace()["is_our_context"]
        async def next_payload():
            return {"entity_id": h.light, "brightness": 100}
        data = SimpleNamespace(entity_id=h.light, context=SimpleNamespace(id="0000000000:cp:AAAA:srvc:00"), max_length=1, initial_sleep=False, force=True, next_service_call_data=next_payload)
        await h.ns["_execute_adaptation_calls"](h.switch, data)
        self.assertEqual(len(h.calls), 1)


class ActivityLoggingTests(unittest.TestCase):
    """The Activity feed records state changes, not every adaptation interval."""

    def setUp(self):
        self.ns = namespace()
        self.ns["EVENT_LOGBOOK_ENTRY"] = "logbook_entry"
        self.ns["ATTR_DOMAIN"] = "domain"
        self.ns["SWITCH_DOMAIN"] = "switch"
        load_functions(self.ns, "switch.py", {"log_activity"}, "CircadianProSwitch")
        load_functions(self.ns, "switch.py", {
            "_notify_manual_state_change", "_log_activity_for_light", "get_manual_control_attributes",
            "set_manual_control_attributes", "add_manual_control_attributes", "reset",
        }, "CircadianProManager")
        self.events = []
        self.context = SimpleNamespace(id="hue-change", user_id=None)
        state = SimpleNamespace(name="Simon's Study", state="on")
        self.hass = SimpleNamespace(
            is_running=True,
            states=SimpleNamespace(get=lambda _: state),
            bus=SimpleNamespace(async_fire=lambda event, data, **kwargs:
                                self.events.append((event, data, kwargs.get("context")))),
        )
        self.switch = SimpleNamespace(
            _name="Simon's Study", entity_id="switch.circadian_pro_simon_s_study",
            lights=["light.study"], is_on=True, hass=self.hass,
        )
        self.switch.log_activity = MethodType(self.ns["log_activity"], self.switch)
        self.switch.activity_writes = 0
        def write_profile_state():
            self.switch.activity_writes += 1
        self.switch.async_write_ha_state = write_profile_state
        self.manager = SimpleNamespace(
            _disabled=False, hass=self.hass, switches=[self.switch],
            manual_control={}, auto_reset_manual_control_times={},
            auto_reset_manual_control_timers={},
            our_last_state_on_change={}, last_service_data={},
            last_service_context={}, last_service_acknowledgements={},
            cancel_ongoing_adaptation_calls=lambda _: None,
            _handle_timer=lambda *args: None,
        )
        for name in ("_notify_manual_state_change", "_log_activity_for_light", "get_manual_control_attributes",
                     "set_manual_control_attributes", "add_manual_control_attributes", "reset"):
            setattr(self.manager, name, MethodType(self.ns[name], self.manager))
        self.flags = self.ns["LightControlAttributes"]

    def test_first_override_and_clear_both_log_once_with_context(self):
        self.manager.set_manual_control_attributes(
            "light.study", self.flags.BRIGHTNESS, context=self.context,
        )
        self.manager.add_manual_control_attributes(
            "light.study", self.flags.COLOR, context=self.context,
        )
        self.assertEqual(len(self.events), 1)
        event, data, context = self.events[0]
        self.assertEqual(event, "logbook_entry")
        self.assertEqual(context, self.context)
        self.assertEqual(data["entity_id"], self.switch.entity_id)
        self.assertEqual(data["domain"], "switch")
        self.assertIn("Manual override detected", data["message"])
        self.manager.reset("light.study", reason="light_off", context=self.context)
        self.manager.reset("light.study", reason="light_off", context=self.context)
        self.assertEqual(len(self.events), 2)
        self.assertEqual(self.switch.activity_writes, 3)
        self.assertIn("light switched off", self.events[1][1]["message"])
        self.assertIs(self.events[1][2], self.context)

    def test_internal_baseline_reset_does_not_clear_manual_flag_or_log(self):
        self.manager.set_manual_control_attributes("light.study", self.flags.ALL)
        self.events.clear()
        self.manager.reset("light.study", reset_manual_control=False)
        self.assertEqual(self.manager.manual_control["light.study"], self.flags.ALL)
        self.assertEqual(self.events, [])

    def test_resumed_by_user_and_timeout_have_distinct_reasons(self):
        for reason, message in (("service", "resumed by user"), ("timeout", "automatic timeout")):
            self.manager.set_manual_control_attributes("light.study", self.flags.ALL)
            self.manager.reset("light.study", reason=reason)
            self.assertIn(message, self.events[-1][1]["message"])
        self.assertEqual(len(self.events), 4)

    def test_explicit_pause_and_resume_log_but_initial_restore_does_not(self):
        ns = self.ns
        load_functions(ns, "switch.py", {"async_turn_on", "async_turn_off"}, "CircadianProSwitch")

        class FakeSwitch:
            @property
            def is_on(self):
                return self._state

        switch = FakeSwitch()
        switch._name = "Simon's Study"
        switch.entity_id = self.switch.entity_id
        switch.hass = self.hass
        switch._state = False
        switch._activity_initialized = False
        switch.lights = ["light.study"]
        switch.initial_transition = 0
        switch.manager = SimpleNamespace(reset=lambda *args, **kwargs: None)
        switch._remove_listeners = lambda: None
        async def setup_listeners():
            return None
        switch._setup_listeners = setup_listeners
        switch.log_activity = MethodType(ns["log_activity"], switch)

        complete_immediate(ns["async_turn_on"](switch, adapt_lights=False))
        self.assertEqual(self.events, [])
        switch._activity_initialized = True
        complete_immediate(ns["async_turn_off"](switch))
        complete_immediate(ns["async_turn_on"](switch, adapt_lights=False))
        self.assertEqual(len(self.events), 2)
        self.assertIn("paused", self.events[0][1]["message"])
        self.assertIn("resumed", self.events[1][1]["message"])

    def test_no_activity_when_integration_is_shutting_down(self):
        self.manager._disabled = True
        self.manager.set_manual_control_attributes("light.study", self.flags.ALL)
        self.manager.reset("light.study")
        self.assertEqual(self.events, [])


class TargetResolutionTests(unittest.TestCase):
    def test_combines_target_selectors_and_filters_non_light_entities(self):
        ns = namespace()
        seen = []
        def extract(hass, target, *, expand_group):
            seen.append((target, expand_group))
            return SimpleNamespace(referenced={"light.a"}, indirectly_referenced={"light.a", "light.b", "switch.unrelated"})
        ns["target_helpers"] = SimpleNamespace(TargetSelection=dict, async_extract_referenced_entity_ids=extract)
        load_functions(ns, "switch.py", {"_get_entity_list"}, "CircadianProManager")
        data = {"entity_id": ["light.a"], "area_id": ["room"], "device_id": ["device"], "floor_id": ["floor"], "label_id": ["label"]}
        manager = SimpleNamespace(hass=SimpleNamespace())
        self.assertEqual(ns["_get_entity_list"](manager, data), ["light.a", "light.b"])
        self.assertEqual(seen, [(data, False)])

    def test_all_target_uses_home_assistant_light_domain(self):
        ns = namespace()
        load_functions(ns, "switch.py", {"_get_entity_list"}, "CircadianProManager")
        domains = []
        def entity_ids(domain):
            domains.append(domain)
            return ["light.b", "light.a"]
        manager = SimpleNamespace(hass=SimpleNamespace(states=SimpleNamespace(async_entity_ids=entity_ids)))
        self.assertEqual(ns["_get_entity_list"](manager, {"entity_id": "all"}), ["light.a", "light.b"])
        self.assertEqual(domains, ["light"])


class BatchAndLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_queued_update_after_profile_off_returns_without_commands(self):
        ns = namespace()
        load_functions(ns, "switch.py", {"_update_attrs_and_maybe_adapt_lights"}, "CircadianProSwitch")
        switch = SimpleNamespace(_name="profile", is_on=False)
        await ns["_update_attrs_and_maybe_adapt_lights"](switch, context=SimpleNamespace(id="queued"))

    async def test_one_solar_snapshot_is_shared_by_the_whole_light_batch(self):
        h = ProtocolHarness(modes=("rgbww",))
        h.ns.update(asyncio=asyncio, is_our_context=lambda *_: False)
        h.ns["is_on"] = lambda *_: True
        load_functions(h.ns, "switch.py", {"_update_attrs_and_maybe_adapt_lights", "_adapt_light", "execute_cancellable_adaptation_calls"}, "CircadianProSwitch")
        h.switch.prepare_adaptation_data = MethodType(h.ns["prepare_switch_adaptation_data"], h.switch)
        h.switch._adapt_light = MethodType(h.ns["_adapt_light"], h.switch)
        h.switch._execute_adaptation_calls = MethodType(h.ns["_execute_adaptation_calls"], h.switch)
        h.switch.execute_cancellable_adaptation_calls = MethodType(h.ns["execute_cancellable_adaptation_calls"], h.switch)
        h.hass.async_create_task = asyncio.create_task
        h.switch.is_on = True
        h.switch._only_once = False
        h.switch._transition = 30
        h.switch._settings = {}
        h.switch._detect_non_ha_changes = False
        h.switch.lights = ["light.a", "light.b", "light.c"]
        h.switch.async_write_ha_state = lambda: None
        h.manager.turn_off_locks = {}
        h.manager.transition_timers = {}
        h.manager.turn_on_event = {}
        h.manager.turn_off_event = {}
        h.manager.adaptation_tasks_brightness = {}
        h.manager.adaptation_tasks_color = {}
        h.manager.cancel_ongoing_adaptation_calls = lambda _: None
        async def no_manual_change(*_):
            pass
        h.manager.update_manually_controlled_from_untracked_change = no_manual_change
        calculations = []
        def get_settings(*args):
            calculations.append(args)
            return {"brightness_pct": 80, "color_temp_kelvin": 4000}
        h.switch._sun_light_settings = SimpleNamespace(get_settings=get_settings, sleep_rgb_or_color_temp="color_temp")
        await asyncio.wait_for(h.ns["_update_attrs_and_maybe_adapt_lights"](h.switch, context=SimpleNamespace(id="batch"), force=True), 5)
        self.assertEqual(len(calculations), 1)
        self.assertEqual(calculations[0], (False, 30))
        self.assertEqual(len(h.calls), 3)
        self.assertEqual({data["entity_id"] for _, _, data in h.calls}, set(h.switch.lights))


if __name__ == "__main__":
    unittest.main()
