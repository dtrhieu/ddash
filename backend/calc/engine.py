"""
Pure calculation functions (placeholders). M4 will implement real logic and tests.
"""

from __future__ import annotations
from datetime import date
from typing import Any, Dict, Iterable, List, Optional, Tuple


def compute_duration(planned_start: date, planned_end: date) -> int:
    """Return duration in days."""
    if planned_end < planned_start:
        return 0
    return (planned_end - planned_start).days


def compute_rig_utilization(items: Iterable[Dict[str, Any]], start: date, end: date) -> float:
    """Placeholder utilization computation; to be implemented in M4."""
    return 0.0


def compute_npt_pct(npt_days: float, duration_days: float) -> float:
    """Placeholder NPT%; to be implemented in M4."""
    if duration_days <= 0:
        return 0.0
    return max(0.0, min(1.0, npt_days / duration_days))


def compute_costs(day_rate: float, duration_days: int, extras: Optional[Dict[str, float]] = None) -> float:
    """Placeholder cost calculation."""
    base = max(0, duration_days) * max(0.0, day_rate)
    extra_sum = sum((extras or {}).values())
    return base + extra_sum


def estimate_eta(planned_end_dates: Iterable[date]) -> Optional[date]:
    """Placeholder ETA as the max planned_end."""
    try:
        return max(planned_end_dates)
    except ValueError:
        return None


def run_all_metrics(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder aggregator. M4 will implement real logic."""
    return {"ok": True, "metrics": {}}
