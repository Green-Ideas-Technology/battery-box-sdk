"""Parser for 0x86 alarm status response."""

from battery_box_sdk.errors import ParseError
from battery_box_sdk.protocol.commands import _RTC_SIZE
from battery_box_sdk.protocol.frames import _AlarmRawFrame

_ALARM_BYTES = 3  # A0 (ltc4015) + A1 (battery) + A2 (system)
_MIN_PAYLOAD = _RTC_SIZE + _ALARM_BYTES


def parse_alarm_frame(payload: bytes) -> _AlarmRawFrame:
    """Parse the data payload from a 0x86 response into an _AlarmRawFrame."""
    if len(payload) < _MIN_PAYLOAD:
        raise ParseError(f"0x86 payload too short: {len(payload)} bytes (need {_MIN_PAYLOAD})")
    off = _RTC_SIZE
    return _AlarmRawFrame(
        raw_ltc4015=payload[off],
        raw_battery=payload[off + 1],
        raw_system=payload[off + 2],
    )
