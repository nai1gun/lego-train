#!/usr/bin/env python3
"""Quick validation of traffic_light_train module."""
import sys
from pathlib import Path

# Add project root to path (works on any machine)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.traffic_light_train import (
    TrafficLightMotorController,
    ControllerState,
    HYSTERESIS_THRESHOLD,
    START_POWER,
    CRUISE_POWER,
    EMERGENCY_STOP_POWER,
)

print("Import OK")
print(f"  HYSTERESIS_THRESHOLD = {HYSTERESIS_THRESHOLD}")
print(f"  START_POWER = {START_POWER}")
print(f"  CRUISE_POWER = {CRUISE_POWER}")
print(f"  EMERGENCY_STOP_POWER = {EMERGENCY_STOP_POWER}")

# Test instantiation
c = TrafficLightMotorController()
print(f"\nInitial state: {c.get_state()}")
assert c.get_state() == ControllerState.UNKNOWN, "Initial state should be UNKNOWN"
assert c.hysteresis_threshold == 3
assert c.start_power == 20
assert c.cruise_power == 50

# Test state transitions (simulate detection)
print("\n--- Simulating green detection ---")
for i in range(5):
    c._update_state("green")
    print(f"  Frame {c._frame_count}: state={c.state.value}, green_counter={c._green_counter}")

assert c.state == ControllerState.MOVING, "Should be MOVING after 3+ green frames"
print(f"  Power after green: {c._compute_power()}%")

# Test state transition to STOPPED
print("\n--- Simulating red detection ---")
for i in range(5):
    c._update_state("red")
    print(f"  Frame {c._frame_count}: state={c.state.value}, red_counter={c._red_counter}")

assert c.state == ControllerState.STOPPED, "Should be STOPPED after 3+ red frames"
print(f"  Power after red: {c._compute_power()}%")

# Test unknown transition
print("\n--- Simulating no_detection ---")
for i in range(5):
    c._update_state("no_detection")
    print(f"  Frame {c._frame_count}: state={c.state.value}, unknown_counter={c._unknown_counter}")

assert c.state == ControllerState.STOPPED, "Should remain STOPPED on unknown"

# Test yellow = go
print("\n--- Simulating yellow detection (should = go) ---")
c2 = TrafficLightMotorController()
for i in range(5):
    c2._update_state("yellow")

assert c2.state == ControllerState.MOVING, "Yellow should trigger MOVING (Yellow = Go policy)"

# Test debug info
debug = c.get_debug_info()
print(f"\nDebug info: {debug}")
assert "frame" in debug
assert "state" in debug
assert "green_counter" in debug
assert "state_history" in debug

print("\n=== ALL TESTS PASSED ===")
