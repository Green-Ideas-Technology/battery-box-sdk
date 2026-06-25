"""Tests for protocol frame parsers using synthetic payload bytes."""

import struct

import pytest

from battery_box_sdk.errors import ParseError
from battery_box_sdk.protocol.parsers import (
    parse_alarm_frame,
    parse_battery_frame,
    parse_charger_frame,
)

# ---------------------------------------------------------------------------
# Helpers for building synthetic payloads
# ---------------------------------------------------------------------------

_RTC = bytes(8)  # 8 zero bytes standing in for the RTC prefix


def _make_charger_payload(
    bat_a_mv: int = 25_000,
    bat_a_ua: int = 1_500,
    bat_b_mv: int = 24_000,
    bat_b_ua: int = 0,
    chg_mv: int = 29_400,
    chg_ma: int = 2_000,
    die_0_1c: int = 320,  # 32.0°C
    aps_status: int = 0,
    act: int = 0,
    slot_status: int = 0x03,
    output_enable: int = 1,
) -> bytes:
    """Build a minimal 0x80 response payload (RTC prefix + status fields)."""
    status = struct.pack(
        "<iiiiiiIHBBB",
        bat_a_mv,
        bat_a_ua,
        bat_b_mv,
        bat_b_ua,
        chg_mv,
        chg_ma,
        die_0_1c,
        aps_status,
        act,
        slot_status,
        output_enable,
    )
    return _RTC + status


def _make_battery_payload(
    battery_id: int = 0,
    soc_pct: int = 85,
    full_charge_mah: int = 47_000,
    bat_total_0_01v: int = 2_160,  # 21.60 V
    charging_count: int = 150,
    ov_alert_low: int = 0x04,  # bit2 = over-voltage protection active
    uv_alert_low: int = 0x00,
) -> bytes:
    """Build a minimal 0x84 response payload."""
    # Header extra: battery_id(1) + bms_polling_status(1) + reserved(2)
    header_extra = bytes([battery_id, 0x00, 0x00, 0x00])
    # 32 cell voltages (uint16), first 6 are 3600 mV, rest zero
    cells = struct.pack("<" + "H" * 32, *([3600] * 6 + [0] * 26))
    # Fields after cell block up to soc (8 × uint16):
    #   max_battery_voltage, min_battery_voltage, pack_voltage, bat_total_voltage,
    #   charging_current_low, discharging_current_low, battery_capacity_lookup, soc
    after_cells = struct.pack(
        "<HHHHHHHH",
        full_charge_mah,  # max_battery_voltage → full charge capacity mAh
        0,  # min_battery_voltage (internal)
        0,  # pack_voltage (internal)
        bat_total_0_01v,  # bat_total_voltage
        0,  # charging_current_low
        0,  # discharging_current_low
        0,  # battery_capacity_lookup
        soc_pct,  # soc
    )
    # 10 more internal uint16 fields: soh, check_code, plc×2, coulomb×4, current_hi×2
    internal_10 = struct.pack("<" + "H" * 10, *([0] * 10))
    # nc[7]
    nc = struct.pack("<" + "H" * 7, *([0] * 7))
    # temp[5]
    temp = struct.pack("<" + "H" * 5, *([0] * 5))
    # charging_count
    count = struct.pack("<H", charging_count)
    # ov_alert_low, ov_alert_high, ov_protect_low, ov_protect_high
    ov_fields = struct.pack("<HHHH", ov_alert_low, 0, 0, 0)
    # uv_alert_low, uv_alert_high, uv_protect_low, uv_protect_high
    uv_fields = struct.pack("<HHHH", uv_alert_low, 0, 0, 0)

    bms = cells + after_cells + internal_10 + nc + temp + count + ov_fields + uv_fields
    return _RTC + header_extra + bms


def _make_alarm_payload(
    raw_ltc4015: int = 0x00,
    raw_battery: int = 0x00,
    raw_system: int = 0x00,
) -> bytes:
    return _RTC + bytes([raw_ltc4015, raw_battery, raw_system])


# ---------------------------------------------------------------------------
# Charger parser tests
# ---------------------------------------------------------------------------


class TestChargerParser:
    def test_basic_fields(self) -> None:
        payload = _make_charger_payload(
            bat_a_mv=25_000, bat_a_ua=1_500, die_0_1c=320, act=0, slot_status=0x03
        )
        frame = parse_charger_frame(payload)
        assert frame.battery_a_voltage_mv == 25_000
        assert frame.battery_a_current_ua == 1_500
        assert frame.die_temperature_0_1c == 320
        assert frame.act == 0
        assert frame.battery_slot_status == 0x03
        assert frame.output_enable == 1

    def test_too_short_raises(self) -> None:
        with pytest.raises(ParseError):
            parse_charger_frame(b"\x00" * 10)

    def test_battery_b_values(self) -> None:
        payload = _make_charger_payload(bat_b_mv=24_500, bat_b_ua=-500)
        frame = parse_charger_frame(payload)
        assert frame.battery_b_voltage_mv == 24_500
        assert frame.battery_b_current_ua == -500


# ---------------------------------------------------------------------------
# Battery parser tests
# ---------------------------------------------------------------------------


class TestBatteryParser:
    def test_basic_fields(self) -> None:
        payload = _make_battery_payload(
            battery_id=0,
            soc_pct=85,
            full_charge_mah=47_000,
            bat_total_0_01v=2_160,
            charging_count=150,
        )
        frame = parse_battery_frame(payload)
        assert frame.battery_id == 0
        assert frame.soc_pct == 85
        assert frame.full_charge_capacity_mah == 47_000
        assert frame.bat_total_voltage_0_01v == 2_160
        assert frame.charging_count == 150

    def test_ov_protection_bit(self) -> None:
        payload = _make_battery_payload(ov_alert_low=0x04)
        frame = parse_battery_frame(payload)
        assert frame.ov_alert_low & 0x04

    def test_uv_protection_clear(self) -> None:
        payload = _make_battery_payload(uv_alert_low=0x00)
        frame = parse_battery_frame(payload)
        assert not (frame.uv_alert_low & 0x08)

    def test_too_short_raises(self) -> None:
        with pytest.raises(ParseError):
            parse_battery_frame(b"\x00" * 10)


# ---------------------------------------------------------------------------
# Alarm parser tests
# ---------------------------------------------------------------------------


class TestAlarmParser:
    def test_all_clear(self) -> None:
        frame = parse_alarm_frame(_make_alarm_payload())
        assert frame.raw_ltc4015 == 0
        assert frame.raw_battery == 0
        assert frame.raw_system == 0

    def test_ltc4015_bits(self) -> None:
        frame = parse_alarm_frame(_make_alarm_payload(raw_ltc4015=0x83))  # bit0+bit1+bit7
        assert frame.raw_ltc4015 & 0x01  # temp > 95°C
        assert frame.raw_ltc4015 & 0x02  # temp > 105°C
        assert frame.raw_ltc4015 & 0x80  # LTC4015 error

    def test_battery_alarm_bits(self) -> None:
        frame = parse_alarm_frame(_make_alarm_payload(raw_battery=0x33))  # bit0+bit1+bit4+bit5
        assert frame.raw_battery & 0x01  # bat A > 65°C
        assert frame.raw_battery & 0x02  # bat A > 75°C
        assert frame.raw_battery & 0x10  # bat B > 65°C
        assert frame.raw_battery & 0x20  # bat B > 75°C

    def test_system_status_bits(self) -> None:
        frame = parse_alarm_frame(_make_alarm_payload(raw_system=0x7F))
        assert frame.raw_system & 0x01  # reboot by ic4015
        assert frame.raw_system & 0x40  # 12V off by battery

    def test_too_short_raises(self) -> None:
        with pytest.raises(ParseError):
            parse_alarm_frame(b"\x00" * 5)
