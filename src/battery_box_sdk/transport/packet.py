"""M3 UART packet building and parsing.

Packet format (both request and response):
  [0]      0xCC  — leading code
  [1..2]   data_len  — uint16 LE, length of the data payload
  [3]      command   — command / response byte
  [4..5]   CRC-16 Modbus of the data payload (LE)
  [6..]    data      — payload (data_len bytes)
"""

from battery_box_sdk.errors import CrcError, InvalidPacketError, UnexpectedCommandError
from battery_box_sdk.transport.crc import crc16_modbus

_LEADING_CODE = 0xCC
_HEADER_SIZE = 6


def build_packet(command: int, data: bytes) -> bytes:
    crc = crc16_modbus(data)
    return (
        bytes(
            [
                _LEADING_CODE,
                len(data) & 0xFF,
                (len(data) >> 8) & 0xFF,
                command,
                crc & 0xFF,
                (crc >> 8) & 0xFF,
            ]
        )
        + data
    )


def parse_packet(raw: bytes, expected_command: int) -> bytes:
    """Validate a response packet and return the payload bytes."""
    if len(raw) < _HEADER_SIZE:
        raise InvalidPacketError(f"Packet too short: {len(raw)} bytes")
    if raw[0] != _LEADING_CODE:
        raise InvalidPacketError(f"Missing leading 0xCC, got 0x{raw[0]:02X}")
    if raw[3] != expected_command:
        raise UnexpectedCommandError(
            f"Expected command 0x{expected_command:02X}, got 0x{raw[3]:02X}"
        )
    data_len = raw[1] | (raw[2] << 8)
    if len(raw) < _HEADER_SIZE + data_len:
        raise InvalidPacketError(
            f"Truncated payload: declared {data_len} bytes, have {len(raw) - _HEADER_SIZE}"
        )
    payload = raw[_HEADER_SIZE : _HEADER_SIZE + data_len]
    declared_crc = raw[4] | (raw[5] << 8)
    actual_crc = crc16_modbus(payload)
    if actual_crc != declared_crc:
        raise CrcError(f"CRC mismatch: expected 0x{declared_crc:04X}, computed 0x{actual_crc:04X}")
    return payload
