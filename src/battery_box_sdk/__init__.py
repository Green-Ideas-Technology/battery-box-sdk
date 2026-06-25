"""battery-box-sdk: Python SDK for reading battery box status over RS485."""

from battery_box_sdk.client import BatteryBoxClient
from battery_box_sdk.config import BatteryBoxConfig
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
from battery_box_sdk.errors import (
    BatteryBoxError,
    CrcError,
    InvalidPacketError,
    ParseError,
    TimeoutError,
    TransportError,
    UnexpectedCommandError,
)

__all__ = [
    "BatteryBoxClient",
    "BatteryBoxConfig",
    "AlarmStatus",
    "BatteryAlarmStatus",
    "BatteryBoxStatus",
    "BatteryPackStatus",
    "BatterySlot",
    "ChargerStatus",
    "Ic4015AlarmStatus",
    "ProtectionStatus",
    "SohEstimate",
    "SystemAlarmStatus",
    "BatteryBoxError",
    "CrcError",
    "InvalidPacketError",
    "ParseError",
    "TimeoutError",
    "TransportError",
    "UnexpectedCommandError",
]
