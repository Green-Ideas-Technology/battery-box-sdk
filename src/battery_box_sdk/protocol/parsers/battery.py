"""Parser for 0x84 BMS battery status response."""

import struct

from battery_box_sdk.errors import ParseError
from battery_box_sdk.protocol.commands import _RTC_SIZE
from battery_box_sdk.protocol.frames import _BatteryRawFrame

# Payload layout after the RTC prefix:
#   uint8  battery_id
#   uint8  bms_polling_status  (internal)
#   2 bytes reserved
#   32 × uint16  bat_cell_voltage  (64 bytes; only first 6 are valid for 6S7P)
#   uint16  max_battery_voltage  (= full charge capacity in mAh)
#   uint16  min_battery_voltage  (= remaining capacity in mAh; internal)
#   uint16  pack_voltage         (= cycle capacity; internal)
#   uint16  bat_total_voltage    (in 0.01V units)
#   uint16  charging_current_low
#   uint16  discharging_current_low
#   uint16  battery_capacity_lookup  (internal)
#   uint16  soc                  (in integer %)
#   ...  (remaining fields are internal / legacy / reserved)
#   (charging_count is at a fixed offset after many more fields)
_HEADER_EXTRA = 1 + 1 + 2  # battery_id + bms_polling_status + reserved
_CELL_BLOCK = 32 * 2  # 64 bytes
_FIELDS_TO_SOC = 4 * 2  # max/min/pack/total (4 × uint16) + 3 more = 7 × uint16 before soc
_MIN_PAYLOAD = _RTC_SIZE + _HEADER_EXTRA + _CELL_BLOCK + 8 * 2  # up to soc

# Offset of charging_count from start of BMS data (after cell block + several uint16 fields)
# Sequence: cell_voltage(64) + max(2)+min(2)+pack(2)+total(2)+ci_low(2)+di_low(2)+cap_lut(2)+soc(2)
#           +soh(2)+check_code(2)+plc(2)+plc2(2)+cc_h(2)+cc_l(2)+dc_h(2)+dc_l(2)+ci_h(2)+di_h(2)
#           +nc[7](14)+temp[5](10)+charging_count(2)
_CHARGING_COUNT_OFFSET_IN_BMS = (
    _CELL_BLOCK
    + 8 * 2  # max/min/pack/total/ci_low/di_low/cap_lut/soc
    + 10 * 2  # soh/check/plc/plc2/cc_h/cc_l/dc_h/dc_l/ci_h/di_h
    + 7 * 2  # nc[7]
    + 5 * 2  # temp[5]
)  # = 64 + 16 + 20 + 14 + 10 = 124

# Offset of ov_alert_low / uv_alert_low from start of BMS data
_OV_ALERT_LOW_OFFSET_IN_BMS = _CHARGING_COUNT_OFFSET_IN_BMS + 2  # after charging_count
_UV_ALERT_LOW_OFFSET_IN_BMS = (
    _OV_ALERT_LOW_OFFSET_IN_BMS + 2 * 4
)  # skip ov_alert_low/high, ov_protect_low/high


def parse_battery_frame(payload: bytes) -> _BatteryRawFrame:
    """Parse the data payload from a 0x84 response into a _BatteryRawFrame."""
    if len(payload) < _MIN_PAYLOAD:
        raise ParseError(f"0x84 payload too short: {len(payload)} bytes (need ≥{_MIN_PAYLOAD})")
    off = _RTC_SIZE
    battery_id = payload[off]
    off += 1
    off += 1  # bms_polling_status (internal)
    off += 2  # reserved

    bms = payload[off:]  # everything from cell block onward

    def _u16_at(o: int) -> int:
        v: int = struct.unpack_from("<H", bms, o)[0]
        return v

    # Public fields we extract:
    full_charge_capacity_mah = _u16_at(_CELL_BLOCK + 0)
    bat_total_voltage_0_01v = _u16_at(_CELL_BLOCK + 6)
    soc_pct = _u16_at(_CELL_BLOCK + 14)

    charging_count = 0
    ov_alert_low = 0
    uv_alert_low = 0

    if len(bms) >= _CHARGING_COUNT_OFFSET_IN_BMS + 2:
        charging_count = _u16_at(_CHARGING_COUNT_OFFSET_IN_BMS)

    if len(bms) >= _OV_ALERT_LOW_OFFSET_IN_BMS + 2:
        ov_alert_low = _u16_at(_OV_ALERT_LOW_OFFSET_IN_BMS)

    if len(bms) >= _UV_ALERT_LOW_OFFSET_IN_BMS + 2:
        uv_alert_low = _u16_at(_UV_ALERT_LOW_OFFSET_IN_BMS)

    return _BatteryRawFrame(
        battery_id=battery_id,
        soc_pct=soc_pct,
        bat_total_voltage_0_01v=bat_total_voltage_0_01v,
        full_charge_capacity_mah=full_charge_capacity_mah,
        charging_count=charging_count,
        ov_alert_low=ov_alert_low,
        uv_alert_low=uv_alert_low,
    )
