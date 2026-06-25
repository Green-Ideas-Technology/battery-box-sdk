"""SOH estimation based on full charge capacity ratio and cycle count."""

from battery_box_sdk.domain.models import SohEstimate

_NOMINAL_CAPACITY_MAH = 49_000

# Source: Battery Box Parameter Manual v0.2.0, SOH cycle count reference table.
_CYCLE_COUNT_SOH_TABLE: list[tuple[int, float]] = [
    (0, 100.0),
    (100, 95.0),
    (200, 92.0),
    (300, 88.0),
    (400, 84.0),
    (500, 80.0),
    (600, 73.0),
    (700, 60.0),
]


def _cycle_count_to_soh_percent(cycle_count: int) -> float:
    if cycle_count <= _CYCLE_COUNT_SOH_TABLE[0][0]:
        return _CYCLE_COUNT_SOH_TABLE[0][1]
    if cycle_count >= _CYCLE_COUNT_SOH_TABLE[-1][0]:
        return _CYCLE_COUNT_SOH_TABLE[-1][1]
    for i in range(len(_CYCLE_COUNT_SOH_TABLE) - 1):
        c0, s0 = _CYCLE_COUNT_SOH_TABLE[i]
        c1, s1 = _CYCLE_COUNT_SOH_TABLE[i + 1]
        if c0 <= cycle_count <= c1:
            ratio = (cycle_count - c0) / (c1 - c0)
            return s0 + ratio * (s1 - s0)
    return _CYCLE_COUNT_SOH_TABLE[-1][1]


def estimate_soh(full_charge_capacity_mah: int, cycle_count: int) -> SohEstimate:
    """Estimate SOH as the lower of capacity ratio and cycle count SOH.

    Per Battery Box Parameter Manual v0.2.0:
      capacity_ratio = full_charge_capacity_mah / 49000 * 100
      cycle_soh      = table lookup (interpolated)
      final_soh      = min(capacity_ratio, cycle_soh)
    """
    capacity_ratio_percent = (full_charge_capacity_mah / _NOMINAL_CAPACITY_MAH) * 100.0
    cycle_count_soh_percent = _cycle_count_to_soh_percent(cycle_count)
    estimated_percent = min(capacity_ratio_percent, cycle_count_soh_percent)
    return SohEstimate(
        estimated_percent=round(estimated_percent, 1),
        capacity_ratio_percent=round(capacity_ratio_percent, 1),
        cycle_count_soh_percent=round(cycle_count_soh_percent, 1),
    )
