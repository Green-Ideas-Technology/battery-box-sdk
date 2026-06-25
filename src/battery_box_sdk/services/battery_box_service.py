"""BatteryBoxService — composes protocol commands into public domain models."""

from __future__ import annotations

from battery_box_sdk.domain.models import (
    AlarmStatus,
    BatteryAlarmStatus,
    BatteryBoxStatus,
    BatteryPackStatus,
    BatterySlot,
    ChargerStatus,
    Ic4015AlarmStatus,
    ProtectionStatus,
    SystemAlarmStatus,
)
from battery_box_sdk.domain.soh import estimate_soh
from battery_box_sdk.protocol import commands as cmd
from battery_box_sdk.protocol.frames import _AlarmRawFrame, _BatteryRawFrame, _ChargerRawFrame
from battery_box_sdk.protocol.parsers import (
    parse_alarm_frame,
    parse_battery_frame,
    parse_charger_frame,
)
from battery_box_sdk.transport.abc import Transport


def _map_charger(raw: _ChargerRawFrame) -> ChargerStatus:
    active: BatterySlot | None
    if raw.act == 0:
        active = BatterySlot.A
    elif raw.act == 1:
        active = BatterySlot.B
    else:
        active = None

    return ChargerStatus(
        battery_a_voltage_v=raw.battery_a_voltage_mv / 1000.0,
        battery_a_current_a=raw.battery_a_current_ma / 1000.0,
        battery_b_voltage_v=raw.battery_b_voltage_mv / 1000.0,
        battery_b_current_a=raw.battery_b_current_ma / 1000.0,
        charging_voltage_v=raw.charging_voltage_mv / 1000.0,
        charging_current_a=raw.charging_current_ma / 1000.0,
        ic_temperature_c=raw.die_temperature_0_1c / 10.0,
        active_battery_slot=active,
        battery_slot_status=raw.battery_slot_status,
        output_enable=bool(raw.output_enable),
    )


def _map_battery(raw: _BatteryRawFrame) -> BatteryPackStatus:
    soh = estimate_soh(raw.full_charge_capacity_mah, raw.charging_count)
    return BatteryPackStatus(
        battery_id=raw.battery_id,
        soc_percent=float(raw.soc_pct),
        bat_total_voltage_v=raw.bat_total_voltage_0_01v / 100.0,
        full_charge_capacity_mah=raw.full_charge_capacity_mah,
        charging_count=raw.charging_count,
        soh=soh,
    )


def _map_alarm(raw: _AlarmRawFrame) -> tuple[AlarmStatus, ProtectionStatus]:
    alarms = AlarmStatus(
        ic4015=Ic4015AlarmStatus(
            temp_over_95c=bool(raw.raw_ltc4015 & 0x01),
            temp_over_105c=bool(raw.raw_ltc4015 & 0x02),
            error=bool(raw.raw_ltc4015 & 0x80),
        ),
        battery=BatteryAlarmStatus(
            a_temp_over_65c=bool(raw.raw_battery & 0x01),
            a_temp_over_75c=bool(raw.raw_battery & 0x02),
            b_temp_over_65c=bool(raw.raw_battery & 0x10),
            b_temp_over_75c=bool(raw.raw_battery & 0x20),
        ),
        system=SystemAlarmStatus(
            reboot_by_ic4015_error=bool(raw.raw_system & 0x01),
            reboot_by_uart_error=bool(raw.raw_system & 0x02),
            stop_by_ic4015_temp=bool(raw.raw_system & 0x04),
            stop_by_battery_a_temp=bool(raw.raw_system & 0x08),
            stop_by_battery_b_temp=bool(raw.raw_system & 0x10),
            output_12v_disabled_by_uart=bool(raw.raw_system & 0x20),
            output_12v_disabled_by_battery=bool(raw.raw_system & 0x40),
        ),
    )
    # ov_alert_low bit2 = pack over-voltage protection
    # uv_alert_low bit3 = pack under-voltage protection
    # These come from the 0x84 battery status frame, not the 0x86 alarm frame.
    # They are injected externally by the caller.
    protections = ProtectionStatus(
        pack_over_voltage=False,
        pack_under_voltage=False,
    )
    return alarms, protections


class BatteryBoxService:
    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def read_status(self) -> BatteryBoxStatus:
        charger_payload = self._t.exchange(cmd.CMD_CHARGER_STATUS, b"\x00", cmd.RESP_CHARGER_STATUS)
        charger_raw = parse_charger_frame(charger_payload)

        bat_a_payload = self._t.exchange(
            cmd.CMD_BATTERY_STATUS,
            bytes([cmd.BATTERY_SLOT_A]),
            cmd.RESP_BATTERY_STATUS,
        )
        bat_a_raw = parse_battery_frame(bat_a_payload)

        bat_b_payload = self._t.exchange(
            cmd.CMD_BATTERY_STATUS,
            bytes([cmd.BATTERY_SLOT_B]),
            cmd.RESP_BATTERY_STATUS,
        )
        bat_b_raw = parse_battery_frame(bat_b_payload)

        alarm_payload = self._t.exchange(cmd.CMD_ALARM_STATUS, b"\x00", cmd.RESP_ALARM_STATUS)
        alarm_raw = parse_alarm_frame(alarm_payload)

        charger = _map_charger(charger_raw)
        bat_a = _map_battery(bat_a_raw)
        bat_b = _map_battery(bat_b_raw)
        alarms, _ = _map_alarm(alarm_raw)

        # Protection bits come from the 0x84 BMS frame (ov_alert_low / uv_alert_low).
        # bit2 = pack over-voltage, bit3 = pack under-voltage.
        # Both batteries should report the same protection state; use battery A.
        protections = ProtectionStatus(
            pack_over_voltage=bool(bat_a_raw.ov_alert_low & 0x04),
            pack_under_voltage=bool(bat_a_raw.uv_alert_low & 0x08),
        )

        return BatteryBoxStatus(
            charger=charger,
            batteries={BatterySlot.A: bat_a, BatterySlot.B: bat_b},
            alarms=alarms,
            protections=protections,
        )

    def read_charger_status(self) -> ChargerStatus:
        payload = self._t.exchange(cmd.CMD_CHARGER_STATUS, b"\x00", cmd.RESP_CHARGER_STATUS)
        return _map_charger(parse_charger_frame(payload))

    def read_battery_status(self, slot: BatterySlot) -> BatteryPackStatus:
        slot_byte = cmd.BATTERY_SLOT_A if slot == BatterySlot.A else cmd.BATTERY_SLOT_B
        payload = self._t.exchange(
            cmd.CMD_BATTERY_STATUS, bytes([slot_byte]), cmd.RESP_BATTERY_STATUS
        )
        return _map_battery(parse_battery_frame(payload))

    def read_alarm_status(self) -> tuple[AlarmStatus, ProtectionStatus]:
        payload = self._t.exchange(cmd.CMD_ALARM_STATUS, b"\x00", cmd.RESP_ALARM_STATUS)
        return _map_alarm(parse_alarm_frame(payload))
