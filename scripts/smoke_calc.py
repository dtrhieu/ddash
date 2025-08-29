#!/usr/bin/env python3
"""
Simple smoke test for the pure calc engine (no Django required).

Usage:
  python3 scripts/smoke_calc.py
"""

from __future__ import annotations

from datetime import date

from backend.calc.engine import (
    compute_costs,
    compute_duration,
    compute_npt_pct,
    estimate_eta,
)


def main() -> None:
    # Duration
    assert compute_duration(date(2025, 1, 1), date(2025, 1, 11)) == 10
    assert compute_duration(date(2025, 1, 11), date(2025, 1, 1)) == 0

    # NPT percent
    assert compute_npt_pct(2.0, 10.0) == 0.2
    assert compute_npt_pct(-5.0, 10.0) == 0.0
    assert compute_npt_pct(5.0, -1.0) == 0.0

    # Costs
    assert compute_costs(1000.0, 10) == 10000.0
    assert compute_costs(1000.0, -5) == 0.0
    assert compute_costs(1000.0, 1, {"mob": 500.0, "demob": 400.0}) == 1900.0

    # ETA
    assert estimate_eta([date(2025, 1, 2), date(2025, 2, 1)]) == date(2025, 2, 1)
    assert estimate_eta([]) is None

    print("Calc engine smoke test passed.")


if __name__ == "__main__":
    main()
