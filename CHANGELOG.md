# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project structure.
- `BatteryBoxClient` facade with `read_status()`, `read_charger_status()`,
  `read_battery_status()`, `read_alarm_status()`, and `calculate_soh()`.
- Domain models: `BatteryBoxStatus`, `BatteryPackStatus`, `ChargerStatus`,
  `AlarmStatus`, `ProtectionStatus`, `SohEstimate`, `BatterySlot`.
- Exception hierarchy: `BatteryBoxError`, `TransportError`, `TimeoutError`,
  `InvalidPacketError`, `CrcError`, `UnexpectedCommandError`, `ParseError`.
- RS485 transport layer with CRC-16 Modbus support.
- Protocol parsers for charger status, battery BMS status, and alarm status.
- SOH estimation based on full charge capacity ratio and cycle count.
