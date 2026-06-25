"""Tests for CRC-16 Modbus."""

from battery_box_sdk.transport.crc import append_crc, crc16_modbus, verify_crc


def test_crc16_known_value() -> None:
    # Algorithm matches rs485_manager.py reference; result bytes [C4, 0B] LE → 0x0BC4
    assert crc16_modbus(b"\x01\x03\x00\x00\x00\x02") == 0x0BC4


def test_append_crc_roundtrip() -> None:
    data = b"\x01\x03\x00\x00\x00\x02"
    packet = append_crc(data)
    assert len(packet) == len(data) + 2
    assert verify_crc(packet)


def test_verify_crc_detects_corruption() -> None:
    data = b"\x01\x03\x00\x00\x00\x02"
    packet = bytearray(append_crc(data))
    packet[0] ^= 0xFF
    assert not verify_crc(bytes(packet))


def test_verify_crc_too_short() -> None:
    assert not verify_crc(b"\x01\x02")
