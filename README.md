# battery-box-sdk

Python SDK for reading battery box status over RS485.

## Requirements

- Python 3.10+
- Linux
- RS485 serial interface

## Installation

Download the wheel from [GitHub Releases](https://github.com/Green-Ideas-Technology/battery-box-sdk/releases) and install:

```bash
pip install battery_box_sdk-0.1.0-py3-none-any.whl
```

Or install directly from a tagged release:

```bash
pip install git+https://github.com/Green-Ideas-Technology/battery-box-sdk.git@v0.1.0
```

## Quick Start

```python
from battery_box_sdk import BatteryBoxClient

client = BatteryBoxClient(port="/dev/ttyLP0", baudrate=115200)
status = client.read_status()

print(status.charger.ic_temperature_c)
print(status.battery_a.soc_percent)
print(status.battery_a.soh.estimated_percent)
print(status.alarms.ic4015.error)
```

## API Reference

See [API reference](docs/api.md) for full documentation.

## Error Handling

`read_status()` raises an exception if any required command fails. All exceptions
are subclasses of `BatteryBoxError`.

```python
from battery_box_sdk import BatteryBoxClient
from battery_box_sdk.errors import BatteryBoxError, TransportError, TimeoutError

try:
    status = client.read_status()
except TimeoutError:
    print("Device did not respond")
except TransportError as e:
    print(f"Serial error: {e}")
except BatteryBoxError as e:
    print(f"SDK error: {e}")
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync
uv run pytest
uv run ruff check
uv run ruff format --check
uv run mypy --strict src
```

## License

MIT
