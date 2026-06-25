"""Internal raw frame dataclasses — not part of the public API."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class _ChargerRawFrame:
    battery_a_voltage_mv: int = 0
    battery_a_current_ma: int = 0
    battery_b_voltage_mv: int = 0
    battery_b_current_ma: int = 0
    charging_voltage_mv: int = 0
    charging_current_ma: int = 0
    die_temperature_0_1c: int = 0
    act: int = 0
    battery_slot_status: int = 0
    output_enable: int = 0


@dataclass
class _BatteryRawFrame:
    battery_id: int = 0
    soc_pct: int = 0
    bat_total_voltage_0_01v: int = 0
    full_charge_capacity_mah: int = 0
    charging_count: int = 0
    ov_alert_low: int = 0
    uv_alert_low: int = 0


@dataclass
class _AlarmRawFrame:
    raw_ltc4015: int = 0
    raw_battery: int = 0
    raw_system: int = 0
