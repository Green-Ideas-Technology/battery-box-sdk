"""Tests for SOH estimation."""

from battery_box_sdk.domain.soh import estimate_soh


def test_soh_full_capacity_new_battery() -> None:
    result = estimate_soh(full_charge_capacity_mah=49_000, cycle_count=0)
    assert result.capacity_ratio_percent == 100.0
    assert result.cycle_count_soh_percent == 100.0
    assert result.estimated_percent == 100.0


def test_soh_limited_by_capacity_ratio() -> None:
    result = estimate_soh(full_charge_capacity_mah=39_200, cycle_count=0)
    assert result.capacity_ratio_percent == pytest.approx(80.0, abs=0.2)
    assert result.estimated_percent == result.capacity_ratio_percent


def test_soh_limited_by_cycle_count() -> None:
    result = estimate_soh(full_charge_capacity_mah=49_000, cycle_count=1000)
    assert result.cycle_count_soh_percent == 75.0
    assert result.estimated_percent == 75.0


def test_soh_takes_lower_value() -> None:
    result = estimate_soh(full_charge_capacity_mah=39_200, cycle_count=800)
    assert result.estimated_percent == min(
        result.capacity_ratio_percent, result.cycle_count_soh_percent
    )


def test_soh_beyond_max_cycles() -> None:
    result = estimate_soh(full_charge_capacity_mah=49_000, cycle_count=2000)
    assert result.cycle_count_soh_percent == 60.0


import pytest
