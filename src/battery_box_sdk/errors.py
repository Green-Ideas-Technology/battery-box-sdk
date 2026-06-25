"""Public exception hierarchy for battery-box-sdk."""


class BatteryBoxError(Exception):
    """Base exception for all battery-box-sdk errors."""


class TransportError(BatteryBoxError):
    """Serial port or I/O error."""


class TimeoutError(BatteryBoxError):
    """Device did not respond within the configured timeout."""


class InvalidPacketError(BatteryBoxError):
    """Received packet does not conform to the expected structure."""


class CrcError(InvalidPacketError):
    """CRC-16 Modbus checksum mismatch."""


class UnexpectedCommandError(InvalidPacketError):
    """Response command code does not match the request."""


class ParseError(BatteryBoxError):
    """Raw frame content could not be parsed into a domain model."""
