"""Parser for 0x80 charger / battery-box status response."""

import struct

from battery_box_sdk.errors import ParseError
from battery_box_sdk.protocol.commands import _RTC_SIZE
from battery_box_sdk.protocol.frames import _ChargerRawFrame

# After skipping the RTC prefix the 4015 status layout is:
#   6 × int32_t  (voltage A/B, current A/B, charging voltage, charging current)
#   1 × uint32_t (die temperature in 0.1°C)
#   1 × uint16_t (aps_status — internal use only)
#   3 × uint8_t  (act, battery_slot_status, output_enable)
_MIN_STATUS_BYTES = 6 * 4 + 1 * 4 + 1 * 2 + 3 * 1  # = 29


def parse_charger_frame(payload: bytes) -> _ChargerRawFrame:
    """Parse the data payload from a 0x80 response into a _ChargerRawFrame."""
    if len(payload) < _RTC_SIZE + _MIN_STATUS_BYTES:
        raise ParseError(
            f"0x80 payload too short: {len(payload)} bytes (need {_RTC_SIZE + _MIN_STATUS_BYTES})"
        )
    data = payload[_RTC_SIZE:]
    off = 0

    def _i32() -> int:
        nonlocal off
        v: int = struct.unpack_from("<i", data, off)[0]
        off += 4
        return v

    def _u32() -> int:
        nonlocal off
        v: int = struct.unpack_from("<I", data, off)[0]
        off += 4
        return v

    def _u16() -> int:
        nonlocal off
        v: int = struct.unpack_from("<H", data, off)[0]
        off += 2
        return v

    def _u8() -> int:
        nonlocal off
        v = data[off]
        off += 1
        return v

    battery_a_voltage_mv = _i32()
    battery_a_current_ma = _i32()
    battery_b_voltage_mv = _i32()
    battery_b_current_ma = _i32()
    charging_voltage_mv = _i32()
    charging_current_ma = _i32()
    die_temperature_0_1c = _u32()
    _u16()  # aps_status — internal, not exposed in public API
    act = _u8()
    battery_slot_status = _u8()
    output_enable = _u8()

    return _ChargerRawFrame(
        battery_a_voltage_mv=battery_a_voltage_mv,
        battery_a_current_ma=battery_a_current_ma,
        battery_b_voltage_mv=battery_b_voltage_mv,
        battery_b_current_ma=battery_b_current_ma,
        charging_voltage_mv=charging_voltage_mv,
        charging_current_ma=charging_current_ma,
        die_temperature_0_1c=die_temperature_0_1c,
        act=act,
        battery_slot_status=battery_slot_status,
        output_enable=output_enable,
    )
