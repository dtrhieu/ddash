from __future__ import annotations

from datetime import date

from calc.engine import compute_duration, compute_npt_pct, estimate_eta


def test_compute_duration_basic():
    assert compute_duration(date(2025, 1, 1), date(2025, 1, 11)) == 10


def test_compute_duration_negative():
    assert compute_duration(date(2025, 1, 11), date(2025, 1, 1)) == 0


def test_npt_pct_bounds():
    assert compute_npt_pct(2.0, 10.0) == 0.2
    assert compute_npt_pct(-5.0, 10.0) == 0.0
    assert compute_npt_pct(5.0, -1.0) == 0.0


def test_estimate_eta():
    assert estimate_eta([date(2025, 1, 2), date(2025, 2, 1)]) == date(2025, 2, 1)
    assert estimate_eta([]) is None
