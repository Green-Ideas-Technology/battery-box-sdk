# battery-box-sdk

Python SDK for reading battery box status over RS485.

**Requirements:** Python 3.10+, Linux, RS485 serial interface.

## Installation

Download the wheel from [GitHub Releases](https://github.com/Green-Ideas-Technology/battery-box-sdk/releases):

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

with BatteryBoxClient(port="/dev/ttyLP0") as client:
    status = client.read_status()

print(f"Battery A SOC: {status.battery_a.soc_percent:.1f} %")
print(f"Battery A SOH: {status.battery_a.soh.estimated_percent:.1f} %")
print(f"Charger temp:  {status.charger.ic_temperature_c:.1f} °C")
```

## Error Handling

`read_status()` raises an exception on any failure — no partial results are returned.

```python
from battery_box_sdk.errors import BatteryBoxError, TimeoutError, TransportError

try:
    status = client.read_status()
except TimeoutError:
    print("Device did not respond")
except TransportError as e:
    print(f"Serial error: {e}")
except BatteryBoxError as e:
    print(f"SDK error: {e}")
```

## API Reference

See **[docs/api.md](docs/api.md)** for the complete API reference including all fields, units, and examples.

## Development

```bash
uv sync
uv run pytest
uv run ruff check src tests
uv run mypy --strict src
```

## License

MIT
