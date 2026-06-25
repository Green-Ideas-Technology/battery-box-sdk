"""Public data models for battery box status."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum


class BatterySlot(Enum):
    A = "A"
    B = "B"


@dataclass(frozen=True)
class SohEstimate:
    estimated_percent: float
    capacity_ratio_percent: float
    cycle_count_soh_percent: float


@dataclass(frozen=True)
class BatteryPackStatus:
    battery_id: int
    soc_percent: float
    bat_total_voltage_v: float
    full_charge_capacity_mah: int
    charging_count: int
    soh: SohEstimate


@dataclass(frozen=True)
class ChargerStatus:
    battery_a_voltage_v: float
    battery_a_current_a: float
    battery_b_voltage_v: float
    battery_b_current_a: float
    charging_voltage_v: float
    charging_current_a: float
    ic_temperature_c: float
    active_battery_slot: BatterySlot | None
    battery_slot_status: int
    output_enable: bool


@dataclass(frozen=True)
class Ic4015AlarmStatus:
    temp_over_95c: bool
    temp_over_105c: bool
    error: bool


@dataclass(frozen=True)
class BatteryAlarmStatus:
    a_temp_over_65c: bool
    a_temp_over_75c: bool
    b_temp_over_65c: bool
    b_temp_over_75c: bool


@dataclass(frozen=True)
class SystemAlarmStatus:
    reboot_by_ic4015_error: bool
    reboot_by_uart_error: bool
    stop_by_ic4015_temp: bool
    stop_by_battery_a_temp: bool
    stop_by_battery_b_temp: bool
    output_12v_disabled_by_uart: bool
    output_12v_disabled_by_battery: bool


@dataclass(frozen=True)
class AlarmStatus:
    ic4015: Ic4015AlarmStatus
    battery: BatteryAlarmStatus
    system: SystemAlarmStatus


@dataclass(frozen=True)
class ProtectionStatus:
    pack_over_voltage: bool
    pack_under_voltage: bool


@dataclass(frozen=True)
class BatteryBoxStatus:
    charger: ChargerStatus
    batteries: Mapping[BatterySlot, BatteryPackStatus]
    alarms: AlarmStatus
    protections: ProtectionStatus

    @property
    def battery_a(self) -> BatteryPackStatus:
        return self.batteries[BatterySlot.A]

    @property
    def battery_b(self) -> BatteryPackStatus:
        return self.batteries[BatterySlot.B]

    @property
    def has_alert(self) -> bool:
        """True if any alarm or protection flag is active."""
        return (
            self.alarms.ic4015.temp_over_95c
            or self.alarms.ic4015.temp_over_105c
            or self.alarms.ic4015.error
            or self.alarms.battery.a_temp_over_65c
            or self.alarms.battery.a_temp_over_75c
            or self.alarms.battery.b_temp_over_65c
            or self.alarms.battery.b_temp_over_75c
            or self.alarms.system.reboot_by_ic4015_error
            or self.alarms.system.reboot_by_uart_error
            or self.alarms.system.stop_by_ic4015_temp
            or self.alarms.system.stop_by_battery_a_temp
            or self.alarms.system.stop_by_battery_b_temp
            or self.alarms.system.output_12v_disabled_by_uart
            or self.alarms.system.output_12v_disabled_by_battery
            or self.protections.pack_over_voltage
            or self.protections.pack_under_voltage
        )
