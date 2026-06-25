"""Tests for CRC-16 Modbus."""

import pytest

from battery_box_sdk.transport.crc import append_crc, crc16_modbus, verify_crc


def test_crc16_known_value() -> None:
    assert crc16_modbus(b"\x01\x03\x00\x00\x00\x02") == 0xC40B


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
