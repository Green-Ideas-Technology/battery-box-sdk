"""Tests for SOH estimation."""

import pytest

from battery_box_sdk.domain.soh import estimate_soh


def test_soh_new_battery_full_capacity() -> None:
    result = estimate_soh(full_charge_capacity_mah=49_000, cycle_count=0)
    assert result.capacity_ratio_percent == 100.0
    assert result.cycle_count_soh_percent == 100.0
    assert result.estimated_percent == 100.0


def test_soh_limited_by_capacity_ratio() -> None:
    # 39200 / 49000 ≈ 80%
    result = estimate_soh(full_charge_capacity_mah=39_200, cycle_count=0)
    assert result.capacity_ratio_percent == pytest.approx(80.0, abs=0.2)
    assert result.estimated_percent == result.capacity_ratio_percent


def test_soh_limited_by_cycle_count() -> None:
    # 500 cycles → 80%; capacity ratio = 100%
    result = estimate_soh(full_charge_capacity_mah=49_000, cycle_count=500)
    assert result.cycle_count_soh_percent == pytest.approx(80.0, abs=0.1)
    assert result.estimated_percent == result.cycle_count_soh_percent


def test_soh_takes_lower_value() -> None:
    result = estimate_soh(full_charge_capacity_mah=39_200, cycle_count=500)
    assert result.estimated_percent == min(
        result.capacity_ratio_percent, result.cycle_count_soh_percent
    )


def test_soh_beyond_max_cycles() -> None:
    result = estimate_soh(full_charge_capacity_mah=49_000, cycle_count=1000)
    assert result.cycle_count_soh_percent == 60.0


def test_soh_interpolation_between_200_and_300() -> None:
    # 250 cycles should interpolate between 92% (200) and 88% (300)
    result = estimate_soh(full_charge_capacity_mah=49_000, cycle_count=250)
    assert result.cycle_count_soh_percent == pytest.approx(90.0, abs=0.1)


def test_soh_exact_lookup_entry() -> None:
    result = estimate_soh(full_charge_capacity_mah=49_000, cycle_count=600)
    assert result.cycle_count_soh_percent == 73.0
