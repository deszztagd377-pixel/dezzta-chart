"""Ingestion coverage tracking (what time ranges are known to be ingested).

A derived bar may be labelled ``complete`` only when its whole bucket lies
inside a covered range and no gap has been carved out of it. Quiet markets
and unknown periods therefore stay ``partial`` rather than being claimed
complete. Ranges are half-open [start_ns, end_ns).
"""
from __future__ import annotations

from typing import Hashable

_MAX_INTERVALS = 5_000


class CoverageTracker:
    def __init__(self, max_intervals: int = _MAX_INTERVALS) -> None:
        self._max = max_intervals
        self._covered: dict[Hashable, list[tuple[int, int]]] = {}
        self.truncated = 0

    def add_covered(self, scope: Hashable, start_ns: int, end_ns: int) -> None:
        if end_ns <= start_ns:
            return
        merged: list[tuple[int, int]] = []
        a, b = start_ns, end_ns
        for s, e in self._covered.get(scope, []):
            if e < a or s > b:
                merged.append((s, e))
            else:
                a, b = min(a, s), max(b, e)
        merged.append((a, b))
        merged.sort()
        if len(merged) > self._max:
            self.truncated += len(merged) - self._max
            merged = merged[-self._max:]
        self._covered[scope] = merged

    def add_gap(self, scope: Hashable, start_ns: int, end_ns: int) -> None:
        if end_ns <= start_ns:
            return
        result: list[tuple[int, int]] = []
        for s, e in self._covered.get(scope, []):
            if e <= start_ns or s >= end_ns:
                result.append((s, e))
                continue
            if s < start_ns:
                result.append((s, start_ns))
            if e > end_ns:
                result.append((end_ns, e))
        self._covered[scope] = result

    def status(self, scope: Hashable, start_ns: int, end_ns: int) -> str:
        """covered | partial | unknown for the range [start_ns, end_ns)."""
        intersects = False
        for s, e in self._covered.get(scope, []):
            if s <= start_ns and e >= end_ns:
                return "covered"
            if s < end_ns and e > start_ns:
                intersects = True
        return "partial" if intersects else "unknown"

    def intervals(self, scope: Hashable) -> list[tuple[int, int]]:
        return list(self._covered.get(scope, []))