"""BatteryBoxClient — public facade for reading battery box status."""

from __future__ import annotations

from battery_box_sdk._logging import _setup_file_logging
from battery_box_sdk.config import BatteryBoxConfig
from battery_box_sdk.domain.models import (
    AlarmStatus,
    BatteryBoxStatus,
    BatteryPackStatus,
    BatterySlot,
    ChargerStatus,
    ProtectionStatus,
    SohEstimate,
)
from battery_box_sdk.domain.soh import estimate_soh
from battery_box_sdk.services.battery_box_service import BatteryBoxService
from battery_box_sdk.transport.abc import Transport
from battery_box_sdk.transport.rs485 import Rs485Transport


class BatteryBoxClient:
    """High-level client for reading battery box status over RS485.

    Usage::

        client = BatteryBoxClient(port="/dev/ttyLP0")
        status = client.read_status()
        print(status.battery_a.soc_percent)
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout_s: float = 2.0,
        *,
        log_dir: str = "/battery_box_sdk/",
        transport: Transport | None = None,
    ) -> None:
        config = BatteryBoxConfig(
            port=port, baudrate=baudrate, timeout_s=timeout_s, log_dir=log_dir
        )
        _setup_file_logging(config.log_dir)
        self._transport: Transport = transport or Rs485Transport(config)
        self._service = BatteryBoxService(self._transport)

    def read_status(self) -> BatteryBoxStatus:
        """Read full battery box status.

        Sends charger, battery A, battery B, and alarm commands in sequence.
        Raises BatteryBoxError (or a subclass) if any command fails.
        """
        return self._service.read_status()

    def read_charger_status(self) -> ChargerStatus:
        """Read charger and battery box status only (0x40 command)."""
        return self._service.read_charger_status()

    def read_battery_status(self, slot: BatterySlot) -> BatteryPackStatus:
        """Read BMS status for a single battery slot (0x44 command)."""
        return self._service.read_battery_status(slot)

    def read_alarm_status(self) -> tuple[AlarmStatus, ProtectionStatus]:
        """Read alarm and protection status (0x46 command)."""
        return self._service.read_alarm_status()

    def calculate_soh(self, full_charge_capacity_mah: int, cycle_count: int) -> SohEstimate:
        """Estimate battery SOH from full charge capacity and cycle count.

        Does not communicate with the device; computation is local.
        """
        return estimate_soh(full_charge_capacity_mah, cycle_count)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> BatteryBoxClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
