"""Tests for packet building and parsing."""

import pytest

from battery_box_sdk.errors import CrcError, InvalidPacketError, UnexpectedCommandError
from battery_box_sdk.transport.packet import build_packet, parse_packet


def _make_response(command: int, payload: bytes) -> bytes:
    """Build a valid response packet from a given command and payload."""
    return build_packet(command, payload)


def test_build_and_parse_roundtrip() -> None:
    payload = b"\x01\x02\x03\x04"
    packet = build_packet(0x80, payload)
    recovered = parse_packet(packet, 0x80)
    assert recovered == payload


def test_leading_code_is_0xcc() -> None:
    packet = build_packet(0x80, b"\x00")
    assert packet[0] == 0xCC


def test_command_byte_position() -> None:
    packet = build_packet(0x84, b"\x00")
    assert packet[3] == 0x84


def test_parse_wrong_command_raises() -> None:
    packet = build_packet(0x80, b"\x00")
    with pytest.raises(UnexpectedCommandError):
        parse_packet(packet, 0x84)


def test_parse_corrupt_crc_raises() -> None:
    packet = bytearray(build_packet(0x80, b"\x01\x02"))
    packet[4] ^= 0xFF  # flip CRC byte
    with pytest.raises(CrcError):
        parse_packet(bytes(packet), 0x80)


def test_parse_too_short_raises() -> None:
    with pytest.raises(InvalidPacketError):
        parse_packet(b"\xcc\x00\x00", 0x80)


def test_parse_wrong_leading_raises() -> None:
    packet = bytearray(build_packet(0x80, b"\x00"))
    packet[0] = 0xAA
    with pytest.raises(InvalidPacketError):
        parse_packet(bytes(packet), 0x80)
