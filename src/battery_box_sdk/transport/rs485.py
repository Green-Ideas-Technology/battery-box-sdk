"""RS485 serial transport using pyserial."""

from __future__ import annotations

import contextlib
import fcntl
import logging

import serial  # type: ignore[import-untyped]

from battery_box_sdk.config import BatteryBoxConfig
from battery_box_sdk.errors import TimeoutError, TransportError
from battery_box_sdk.transport.abc import Transport
from battery_box_sdk.transport.packet import _HEADER_SIZE, build_packet, parse_packet

logger = logging.getLogger(__name__)


class Rs485Transport(Transport):
    def __init__(self, config: BatteryBoxConfig) -> None:
        self._config = config
        try:
            self._serial = serial.Serial(
                port=config.port,
                baudrate=config.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=config.timeout_s,
            )
            fcntl.flock(self._serial.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except serial.SerialException as exc:
            raise TransportError(str(exc)) from exc
        except OSError as exc:
            raise TransportError(f"Could not lock {config.port}: {exc}") from exc

    def exchange(self, command: int, data: bytes, expected_response: int) -> bytes:
        packet = build_packet(command, data)
        logger.debug("TX cmd=0x%02X  packet=%s", command, packet.hex())
        try:
            self._serial.reset_input_buffer()
            self._serial.write(packet)
            # Phase 1: read fixed 6-byte header to learn payload length
            header = self._serial.read(_HEADER_SIZE)
            if len(header) < _HEADER_SIZE:
                logger.error(
                    "Timeout: no response to cmd=0x%02X (got %d/%d header bytes)",
                    command, len(header), _HEADER_SIZE,
                )
                raise TimeoutError(f"No response to command 0x{command:02X}")
            # Phase 2: read exactly the declared payload — returns as soon as all bytes arrive
            data_len = header[1] | (header[2] << 8)
            payload_bytes = self._serial.read(data_len) if data_len else b""
            if len(payload_bytes) < data_len:
                logger.error(
                    "Timeout: truncated response for cmd=0x%02X (got %d/%d payload bytes)",
                    command, len(payload_bytes), data_len,
                )
                raise TimeoutError(f"Truncated response for command 0x{command:02X}")
        except serial.SerialTimeoutException as exc:
            logger.error("Serial timeout for cmd=0x%02X: %s", command, exc)
            raise TimeoutError(str(exc)) from exc
        except serial.SerialException as exc:
            logger.error("Serial error for cmd=0x%02X: %s", command, exc)
            raise TransportError(str(exc)) from exc
        raw = header + payload_bytes
        logger.debug("RX cmd=0x%02X  raw=%s", expected_response, raw.hex())
        return parse_packet(raw, expected_response)

    def close(self) -> None:
        if self._serial.is_open:
            with contextlib.suppress(OSError):
                fcntl.flock(self._serial.fileno(), fcntl.LOCK_UN)
            self._serial.close()
