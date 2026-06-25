"""RS485 serial transport using pyserial."""

from __future__ import annotations

import serial  # type: ignore[import-untyped]

from battery_box_sdk.config import BatteryBoxConfig
from battery_box_sdk.errors import TimeoutError, TransportError
from battery_box_sdk.transport.abc import Transport
from battery_box_sdk.transport.crc import append_crc, verify_crc


class Rs485Transport(Transport):
    def __init__(self, config: BatteryBoxConfig) -> None:
        self._config = config
        try:
            self._serial = serial.Serial(
                port=config.port,
                baudrate=config.baudrate,
                timeout=config.timeout_s,
            )
        except serial.SerialException as exc:
            raise TransportError(str(exc)) from exc

    def send_command(self, command: bytes) -> bytes:
        packet = append_crc(command)
        try:
            self._serial.write(packet)
            response = self._serial.read(256)
        except serial.SerialTimeoutException as exc:
            raise TimeoutError(str(exc)) from exc
        except serial.SerialException as exc:
            raise TransportError(str(exc)) from exc
        if not response:
            raise TimeoutError("No response received")
        if not verify_crc(response):
            from battery_box_sdk.errors import CrcError
            raise CrcError("CRC mismatch in response")
        return response[:-2]

    def close(self) -> None:
        if self._serial.is_open:
            self._serial.close()
