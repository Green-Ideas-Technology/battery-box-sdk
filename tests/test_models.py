"""Tests for BatteryBoxStatus.has_alert aggregation property."""

import pytest

from battery_box_sdk.domain.models import (
    AlarmStatus,
    BatteryAlarmStatus,
    BatteryBoxStatus,
    BatteryPackStatus,
    BatterySlot,
    ChargerStatus,
    Ic4015AlarmStatus,
    ProtectionStatus,
    SohEstimate,
    SystemAlarmStatus,
)

_ALL_CLEAR_IC4015 = Ic4015AlarmStatus(temp_over_95c=False, temp_over_105c=False, error=False)
_ALL_CLEAR_BATTERY = BatteryAlarmStatus(
    a_temp_over_65c=False,
    a_temp_over_75c=False,
    b_temp_over_65c=False,
    b_temp_over_75c=False,
)
_ALL_CLEAR_SYSTEM = SystemAlarmStatus(
    reboot_by_ic4015_error=False,
    reboot_by_uart_error=False,
    stop_by_ic4015_temp=False,
    stop_by_battery_a_temp=False,
    stop_by_battery_b_temp=False,
    output_12v_disabled_by_uart=False,
    output_12v_disabled_by_battery=False,
)
_ALL_CLEAR_PROTECTIONS = ProtectionStatus(pack_over_voltage=False, pack_under_voltage=False)


def _make_status(
    ic4015: Ic4015AlarmStatus = _ALL_CLEAR_IC4015,
    battery_alarm: BatteryAlarmStatus = _ALL_CLEAR_BATTERY,
    system: SystemAlarmStatus = _ALL_CLEAR_SYSTEM,
    protections: ProtectionStatus = _ALL_CLEAR_PROTECTIONS,
) -> BatteryBoxStatus:
    soh = SohEstimate(
        estimated_percent=100.0,
        capacity_ratio_percent=100.0,
        cycle_count_soh_percent=100.0,
    )
    pack = BatteryPackStatus(
        battery_id=0,
        soc_percent=100.0,
        bat_total_voltage_v=25.0,
        full_charge_capacity_mah=49_000,
        charging_count=0,
        soh=soh,
    )
    charger = ChargerStatus(
        battery_a_voltage_v=25.0,
        battery_a_current_a=0.0,
        battery_b_voltage_v=25.0,
        battery_b_current_a=0.0,
        charging_voltage_v=29.4,
        charging_current_a=2.0,
        ic_temperature_c=30.0,
        active_battery_slot=BatterySlot.A,
        battery_slot_status=0x03,
        output_enable=True,
    )
    return BatteryBoxStatus(
        charger=charger,
        batteries={BatterySlot.A: pack, BatterySlot.B: pack},
        alarms=AlarmStatus(ic4015=ic4015, battery=battery_alarm, system=system),
        protections=protections,
    )


def test_has_alert_all_clear() -> None:
    assert not _make_status().has_alert


@pytest.mark.parametrize(
    "ic4015",
    [
        Ic4015AlarmStatus(temp_over_95c=True, temp_over_105c=False, error=False),
        Ic4015AlarmStatus(temp_over_95c=False, temp_over_105c=True, error=False),
        Ic4015AlarmStatus(temp_over_95c=False, temp_over_105c=False, error=True),
    ],
)
def test_has_alert_ic4015(ic4015: Ic4015AlarmStatus) -> None:
    assert _make_status(ic4015=ic4015).has_alert


@pytest.mark.parametrize(
    "battery_alarm",
    [
        BatteryAlarmStatus(a_temp_over_65c=True, a_temp_over_75c=False, b_temp_over_65c=False, b_temp_over_75c=False),  # noqa: E501
        BatteryAlarmStatus(a_temp_over_65c=False, a_temp_over_75c=True, b_temp_over_65c=False, b_temp_over_75c=False),  # noqa: E501
        BatteryAlarmStatus(a_temp_over_65c=False, a_temp_over_75c=False, b_temp_over_65c=True, b_temp_over_75c=False),  # noqa: E501
        BatteryAlarmStatus(a_temp_over_65c=False, a_temp_over_75c=False, b_temp_over_65c=False, b_temp_over_75c=True),  # noqa: E501
    ],
)
def test_has_alert_battery_alarm(battery_alarm: BatteryAlarmStatus) -> None:
    assert _make_status(battery_alarm=battery_alarm).has_alert


def _sys(*, reboot_ic4015: bool = False, reboot_uart: bool = False,
         stop_ic4015: bool = False, stop_bat_a: bool = False, stop_bat_b: bool = False,
         off_uart: bool = False, off_battery: bool = False) -> SystemAlarmStatus:
    return SystemAlarmStatus(
        reboot_by_ic4015_error=reboot_ic4015,
        reboot_by_uart_error=reboot_uart,
        stop_by_ic4015_temp=stop_ic4015,
        stop_by_battery_a_temp=stop_bat_a,
        stop_by_battery_b_temp=stop_bat_b,
        output_12v_disabled_by_uart=off_uart,
        output_12v_disabled_by_battery=off_battery,
    )


@pytest.mark.parametrize(
    "system",
    [
        _sys(reboot_ic4015=True),
        _sys(reboot_uart=True),
        _sys(stop_ic4015=True),
        _sys(stop_bat_a=True),
        _sys(stop_bat_b=True),
        _sys(off_uart=True),
        _sys(off_battery=True),
    ],
)
def test_has_alert_system(system: SystemAlarmStatus) -> None:
    assert _make_status(system=system).has_alert


def test_has_alert_pack_over_voltage() -> None:
    assert _make_status(
        protections=ProtectionStatus(pack_over_voltage=True, pack_under_voltage=False)
    ).has_alert


def test_has_alert_pack_under_voltage() -> None:
    assert _make_status(
        protections=ProtectionStatus(pack_over_voltage=False, pack_under_voltage=True)
    ).has_alert
