"""Configuration for BatteryBoxClient."""

from dataclasses import dataclass, field


@dataclass
class BatteryBoxConfig:
    port: str
    baudrate: int = 115200
    timeout_s: float = 2.0
    retries: int = 3
    device_address: int = field(default=0x01)
