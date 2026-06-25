# battery-box-sdk

Python SDK for reading battery box status over RS485.

**Requirements:** Python 3.10+, Linux, RS485 serial interface.

---

## Installation

### From wheel (recommended)

Download the `.whl` from [GitHub Releases](https://github.com/Green-Ideas-Technology/battery-box-sdk/releases):

```bash
pip install battery_box_sdk-0.1.0-py3-none-any.whl
```

### From source

```bash
pip install git+https://github.com/Green-Ideas-Technology/battery-box-sdk.git@v0.1.0
```

---

## Quick Start

```python
from battery_box_sdk import BatteryBoxClient

with BatteryBoxClient(port="/dev/ttyLP0") as client:
    status = client.read_status()

print(f"Battery A SOC: {status.battery_a.soc_percent:.1f} %")
print(f"Battery A SOH: {status.battery_a.soh.estimated_percent:.1f} %")
print(f"Charger temp:  {status.charger.ic_temperature_c:.1f} °C")
```

---

## BatteryBoxClient

```python
from battery_box_sdk import BatteryBoxClient
```

The main entry point. Manages the serial connection and exposes high-level read methods.

### Constructor

```python
BatteryBoxClient(
    port: str,
    baudrate: int = 115200,
    timeout_s: float = 2.0,
)
```

| Parameter | Description |
| --- | --- |
| `port` | Serial device path, e.g. `"/dev/ttyLP0"` |
| `baudrate` | Baud rate (default `115200`) |
| `timeout_s` | Per-command response timeout in seconds (default `2.0`) |

Supports use as a context manager (`with` statement) — `close()` is called automatically on exit.

### Methods

#### `read_status() → BatteryBoxStatus`

Read complete battery box status in one call. Sends four commands sequentially (charger, battery A, battery B, alarm). Raises `BatteryBoxError` on any failure — no partial results are returned.

#### `read_charger_status() → ChargerStatus`

Read charger and output status only.

#### `read_battery_status(slot: BatterySlot) → BatteryPackStatus`

Read BMS status for a single battery slot.

```python
from battery_box_sdk import BatteryBoxClient, BatterySlot

status = client.read_battery_status(BatterySlot.A)
```

#### `read_alarm_status() → tuple[AlarmStatus, ProtectionStatus]`

Read alarm and protection flags only.

#### `calculate_soh(full_charge_capacity_mah: int, cycle_count: int) → SohEstimate`

Estimate SOH from already-read values. Does not communicate with the device.

#### `close() → None`

Release the serial port.

---

## Data Models

All models are **frozen dataclasses** (immutable). Import them from `battery_box_sdk`:

```python
from battery_box_sdk import (
    BatteryBoxStatus, BatteryPackStatus, ChargerStatus,
    AlarmStatus, ProtectionStatus, SohEstimate, BatterySlot,
)
```

### BatteryBoxStatus

Returned by `read_status()`.

| Field | Type | Description |
| --- | --- | --- |
| `charger` | `ChargerStatus` | Charger and output status |
| `batteries` | `Mapping[BatterySlot, BatteryPackStatus]` | BMS status keyed by slot |
| `alarms` | `AlarmStatus` | Alarm flags |
| `protections` | `ProtectionStatus` | Hardware protection flags |
| `battery_a` | `BatteryPackStatus` | Shortcut for `batteries[BatterySlot.A]` |
| `battery_b` | `BatteryPackStatus` | Shortcut for `batteries[BatterySlot.B]` |
| `has_alert` | `bool` | `True` if any alarm or protection flag is active |

### BatteryPackStatus

BMS data for one battery pack.

| Field | Type | Unit | Description |
| --- | --- | --- | --- |
| `battery_id` | `int` | — | Battery identifier reported by BMS |
| `soc_percent` | `float` | % | State of charge (0–100) |
| `bat_total_voltage_v` | `float` | V | Pack total voltage |
| `full_charge_capacity_mah` | `int` | mAh | Full charge capacity measured by BMS |
| `charging_count` | `int` | cycles | Charge cycle count |
| `soh` | `SohEstimate` | — | State of health estimate |

### SohEstimate

| Field | Type | Description |
| --- | --- | --- |
| `estimated_percent` | `float` | Final SOH estimate (minimum of the two signals below) |
| `capacity_ratio_percent` | `float` | SOH based on capacity fade vs. nominal 49 000 mAh |
| `cycle_count_soh_percent` | `float` | SOH based on cycle count lookup table |

### ChargerStatus

| Field | Type | Unit | Description |
| --- | --- | --- | --- |
| `battery_a_voltage_v` | `float` | V | Battery A terminal voltage measured at charger |
| `battery_a_current_a` | `float` | A | Battery A charge/discharge current (negative = discharging) |
| `battery_b_voltage_v` | `float` | V | Battery B terminal voltage |
| `battery_b_current_a` | `float` | A | Battery B current |
| `charging_voltage_v` | `float` | V | Charger output voltage |
| `charging_current_a` | `float` | A | Charger output current |
| `ic_temperature_c` | `float` | °C | Charger IC die temperature |
| `active_battery_slot` | `BatterySlot \| None` | — | Slot currently being charged, or `None` |
| `battery_a_present` | `bool` | — | Battery A is physically installed |
| `battery_b_present` | `bool` | — | Battery B is physically installed |
| `output_enable` | `bool` | — | Whether the 12 V output is enabled |

### AlarmStatus

Groups three alarm sources.

```text
AlarmStatus
├── ic4015: Ic4015AlarmStatus
├── battery: BatteryAlarmStatus
└── system: SystemAlarmStatus
```

#### Ic4015AlarmStatus

| Field | Type | Description |
| --- | --- | --- |
| `temp_over_95c` | `bool` | IC die temperature exceeded 95 °C |
| `temp_over_105c` | `bool` | IC die temperature exceeded 105 °C |
| `error` | `bool` | IC reported a fault |

#### BatteryAlarmStatus

| Field | Type | Description |
| --- | --- | --- |
| `a_temp_over_65c` | `bool` | Battery A temperature exceeded 65 °C |
| `a_temp_over_75c` | `bool` | Battery A temperature exceeded 75 °C |
| `b_temp_over_65c` | `bool` | Battery B temperature exceeded 65 °C |
| `b_temp_over_75c` | `bool` | Battery B temperature exceeded 75 °C |

#### SystemAlarmStatus

| Field | Type | Description |
| --- | --- | --- |
| `reboot_by_ic4015_error` | `bool` | System rebooted due to IC fault |
| `reboot_by_uart_error` | `bool` | System rebooted due to UART error |
| `stop_by_ic4015_temp` | `bool` | Output stopped due to IC overtemperature |
| `stop_by_battery_a_temp` | `bool` | Output stopped due to battery A overtemperature |
| `stop_by_battery_b_temp` | `bool` | Output stopped due to battery B overtemperature |
| `output_12v_disabled_by_uart` | `bool` | 12 V output disabled by UART command |
| `output_12v_disabled_by_battery` | `bool` | 12 V output disabled due to battery fault |

### ProtectionStatus

Hardware protection flags from the BMS.

| Field | Type | Description |
| --- | --- | --- |
| `pack_over_voltage` | `bool` | Pack over-voltage protection active |
| `pack_under_voltage` | `bool` | Pack under-voltage protection active |

### BatterySlot

```python
class BatterySlot(Enum):
    A = "A"
    B = "B"
```

---

## Exception Hierarchy

All exceptions inherit from `BatteryBoxError`.

```text
BatteryBoxError
├── TransportError          — serial port / I/O failure
├── TimeoutError            — device did not respond within timeout_s
├── InvalidPacketError      — malformed response packet
│   ├── CrcError            — CRC-16 checksum mismatch
│   └── UnexpectedCommandError — response command code mismatch
└── ParseError              — frame content could not be decoded
```

```python
from battery_box_sdk.errors import (
    BatteryBoxError,
    TransportError,
    TimeoutError,
    InvalidPacketError,
    CrcError,
    UnexpectedCommandError,
    ParseError,
)
```

---

## Usage Examples

### Basic read

```python
from battery_box_sdk import BatteryBoxClient

with BatteryBoxClient(port="/dev/ttyLP0") as client:
    status = client.read_status()

print(f"Battery A SOC: {status.battery_a.soc_percent:.1f} %")
print(f"Battery B SOC: {status.battery_b.soc_percent:.1f} %")
print(f"Battery A SOH: {status.battery_a.soh.estimated_percent:.1f} %")
print(f"Charger temp:  {status.charger.ic_temperature_c:.1f} °C")
```

### Error handling

```python
from battery_box_sdk import BatteryBoxClient
from battery_box_sdk.errors import BatteryBoxError, TimeoutError, TransportError

with BatteryBoxClient(port="/dev/ttyLP0", timeout_s=3.0) as client:
    try:
        status = client.read_status()
    except TimeoutError:
        print("Device did not respond")
    except TransportError as e:
        print(f"Serial error: {e}")
    except BatteryBoxError as e:
        print(f"SDK error: {e}")
```

### Check alarms and protections

```python
status = client.read_status()

if status.protections.pack_over_voltage:
    print("WARNING: pack over-voltage protection active")

if status.protections.pack_under_voltage:
    print("WARNING: pack under-voltage protection active")

if status.alarms.ic4015.error:
    print("ALARM: charger IC fault")

if status.alarms.battery.a_temp_over_75c:
    print("ALARM: battery A critical overtemperature (>75°C)")
```

### SOH monitoring

```python
status = client.read_status()
soh_a = status.battery_a.soh

print(f"Estimated SOH: {soh_a.estimated_percent:.1f} %")
print(f"  Capacity-based: {soh_a.capacity_ratio_percent:.1f} %")
print(f"  Cycle-based:    {soh_a.cycle_count_soh_percent:.1f} %")
print(f"Charge cycles:  {status.battery_a.charging_count}")
```

### Identify active charging slot

```python
status = client.read_status()
slot = status.charger.active_battery_slot

if slot is None:
    print("No battery currently charging")
else:
    print(f"Charging battery {slot.value}")
    print(f"  Charging voltage: {status.charger.charging_voltage_v:.2f} V")
    print(f"  Charging current: {status.charger.charging_current_a:.2f} A")
```

---

## Development

```bash
uv sync
uv run pytest
uv run ruff check src tests
uv run mypy --strict src
```

## License

MIT
