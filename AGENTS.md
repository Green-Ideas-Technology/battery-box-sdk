# AGENTS.md

## Project Overview

`battery-box-sdk` is a public Python SDK for reading battery box status over RS485.

Distribution name: `battery-box-sdk`
Import package: `battery_box_sdk`
Target: Linux Python 3.10+

## Development Rules

### Public API Boundary

- Public API covers only the parameters documented in the official Battery Box
  Parameter Manual (v0.2.0 or later).
- Do NOT expose raw frame fields, reserved fields, legacy field names, or
  internal parser state in any public model.
- Do NOT copy or reference internal BMS protocol documents, M3 firmware source
  code, UART Excel files, or the internal parameter mapping table.
- New public API fields require a corresponding update to the official parameter
  manual before being added to the SDK.

### Adding New Public Fields

1. Confirm the field is documented in the official parameter manual.
2. Update the internal parser / mapper.
3. Update the public domain model.
4. Add or update tests.
5. Update README / examples and CHANGELOG.
6. Release following semantic versioning.

### Confidentiality

This is a public repository. Never commit:

- Internal BMS protocol specifications.
- M3 firmware C source code or headers.
- UART command Excel files.
- Internal parameter mapping tables.
- Customer upload API credentials or endpoint URLs.
- Any file from the internal parameter-manual repository.

### Code Style

- `mypy --strict src` must pass.
- `ruff check` and `ruff format --check` must pass.
- `pytest` must pass.
- No print statements in library code; use logging at DEBUG level if needed.
- No comments that describe what the code does; only add comments for
  non-obvious constraints or workarounds.

### Error Handling

- `read_status()` raises an exception if any required command fails.
  Never return partial results.
- All public exceptions are subclasses of `BatteryBoxError`.

### Testing

- Fake transport must be substitutable for real RS485 transport.
- Fixture bytes for parser tests must be documented with their source frame
  type (e.g., `0x80 charger status response`), but must NOT reference internal
  register addresses or protocol document page numbers.

## Project Structure

```text
src/
  battery_box_sdk/
    __init__.py       # public exports
    client.py         # BatteryBoxClient facade
    config.py         # BatteryBoxConfig
    errors.py         # exception hierarchy
    py.typed
    transport/        # serial port, CRC, packet I/O
    protocol/         # raw frame parsers
    domain/           # public data models, SOH calculation
    services/         # high-level operations
examples/
tests/
```

## Quality Gate

Before any release:

```bash
uv sync --locked
uv run pytest
uv run ruff check
uv run ruff format --check
uv run mypy --strict src
uv build --wheel
```
