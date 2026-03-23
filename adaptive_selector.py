from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from dataclasses import asdict, dataclass
from typing import Any, Sequence

from algorithms.searching import SEARCHING_LABELS
from algorithms.sorting import SORTING_LABELS


@dataclass(frozen=True)
class SortInputProfile:
    size: int
    is_sorted: bool
    is_reverse_sorted: bool
    disorder_ratio: float
    unique_ratio: float


@dataclass(frozen=True)
class SearchInputProfile:
    size: int
    is_sorted: bool
    repeated_queries: bool
    target_position_hint: str


@dataclass(frozen=True)
class Recommendation:
    algorithm_key: str
    rationale: str
    profile: dict[str, Any]

    @property
    def label(self) -> str:
        return SORTING_LABELS.get(
            self.algorithm_key, SEARCHING_LABELS.get(self.algorithm_key, self.algorithm_key)
        )


RESULTS_PATH = Path(__file__).resolve().with_name("results.csv")


def is_non_decreasing(values: Sequence[int]) -> bool:
    return all(left <= right for left, right in zip(values, values[1:]))


def analyze_sorting_input(values: Sequence[int]) -> SortInputProfile:
    size = len(values)
    if size < 2:
        return SortInputProfile(
            size=size,
            is_sorted=True,
            is_reverse_sorted=True,
            disorder_ratio=0.0,
            unique_ratio=1.0 if size else 0.0,
        )

    disorder_pairs = sum(1 for left, right in zip(values, values[1:]) if left > right)
    reverse_pairs = sum(1 for left, right in zip(values, values[1:]) if left < right)
    unique_ratio = len(set(values)) / size

    return SortInputProfile(
        size=size,
        is_sorted=disorder_pairs == 0,
        is_reverse_sorted=reverse_pairs == 0,
        disorder_ratio=disorder_pairs / (size - 1),
        unique_ratio=unique_ratio,
    )


def recommend_sort_algorithm(values: Sequence[int]) -> Recommendation:
    profile = analyze_sorting_input(values)

    if profile.size <= 32:
        rationale = "Tiny inputs are dominated by constant overhead, so insertion sort is the lightest option."
        return Recommendation("insertion", rationale, asdict(profile))

    empirical_choice = lookup_empirical_sort_choice(profile)
    if empirical_choice is not None:
        dataset_type = classify_sort_dataset(profile)
        rationale = (
            "This matches the fastest measured result from the local benchmark for "
            f"{dataset_type} data near size {profile.size}."
        )
        return Recommendation(empirical_choice, rationale, asdict(profile))

    if profile.disorder_ratio <= 0.08 and profile.size <= 4096:
        rationale = "The list is nearly sorted, so insertion sort can finish with very few element shifts."
        return Recommendation("insertion", rationale, asdict(profile))

    if profile.is_reverse_sorted and profile.size >= 256:
        rationale = "A strongly descending input benefits from merge sort's predictable divide-and-conquer behavior."
        return Recommendation("merge", rationale, asdict(profile))

    if profile.unique_ratio <= 0.25 and profile.size >= 1024:
        rationale = "The data has many duplicates, so merge sort avoids uneven partitions and stays consistent."
        return Recommendation("merge", rationale, asdict(profile))

    rationale = "This looks like a general-purpose case, so quick sort is the strongest default in this project."
    return Recommendation("quick", rationale, asdict(profile))


def analyze_search_input(
    values: Sequence[int],
    *,
    assume_sorted: bool | None = None,
    repeated_queries: bool = False,
    target_position_hint: str = "unknown",
) -> SearchInputProfile:
    return SearchInputProfile(
        size=len(values),
        is_sorted=is_non_decreasing(values) if assume_sorted is None else assume_sorted,
        repeated_queries=repeated_queries,
        target_position_hint=target_position_hint,
    )


def recommend_search_algorithm(
    values: Sequence[int],
    *,
    assume_sorted: bool | None = None,
    repeated_queries: bool = False,
    target_position_hint: str = "unknown",
) -> Recommendation:
    profile = analyze_search_input(
        values,
        assume_sorted=assume_sorted,
        repeated_queries=repeated_queries,
        target_position_hint=target_position_hint,
    )

    if profile.size == 0:
        rationale = "Empty input returns immediately, so the simplest search path is enough."
        return Recommendation("linear", rationale, asdict(profile))

    if not profile.is_sorted:
        rationale = "The input is not sorted, so linear search is the only valid option without preprocessing."
        return Recommendation("linear", rationale, asdict(profile))

    if profile.size <= 32:
        rationale = "On very small sorted arrays, linear search stays competitive and keeps overhead minimal."
        return Recommendation("linear", rationale, asdict(profile))

    empirical_choice = lookup_empirical_search_choice(profile)
    if empirical_choice is not None:
        rationale = (
            "This matches the fastest measured result from the local benchmark for "
            f"sorted data near size {profile.size}."
        )
        return Recommendation(empirical_choice, rationale, asdict(profile))

    if profile.target_position_hint == "front":
        rationale = "The target is expected near the front, which favors exponential search."
        return Recommendation("exponential", rationale, asdict(profile))

    rationale = "Sorted input favors logarithmic search, and binary search is the strongest general-purpose choice."
    return Recommendation("binary", rationale, asdict(profile))


def classify_sort_dataset(profile: SortInputProfile) -> str:
    if profile.is_sorted:
        return "sorted"
    if profile.is_reverse_sorted:
        return "reverse"
    if profile.unique_ratio <= 0.25:
        return "few_unique"
    if profile.disorder_ratio <= 0.15:
        return "nearly_sorted"
    return "random"


def lookup_empirical_sort_choice(profile: SortInputProfile) -> str | None:
    dataset_type = classify_sort_dataset(profile)
    return lookup_empirical_choice(
        kind="sorting",
        dataset_type=dataset_type,
        size=profile.size,
        scenario="-",
    )


def lookup_empirical_search_choice(profile: SearchInputProfile) -> str | None:
    scenario = profile.target_position_hint if profile.target_position_hint != "unknown" else "middle"
    return lookup_empirical_choice(
        kind="searching",
        dataset_type="sorted",
        size=profile.size,
        scenario=scenario,
    )


def lookup_empirical_choice(
    *, kind: str, dataset_type: str, size: int, scenario: str
) -> str | None:
    winners = load_empirical_winners()
    matching = [
        candidate
        for candidate in winners
        if candidate[0] == kind and candidate[1] == dataset_type and candidate[3] == scenario
    ]
    if not matching:
        return None

    closest = min(matching, key=lambda candidate: (abs(candidate[2] - size), candidate[2]))
    return winners[closest]


@lru_cache(maxsize=1)
def load_empirical_winners() -> dict[tuple[str, str, int, str], str]:
    if not RESULTS_PATH.exists():
        return {}

    best_rows: dict[tuple[str, str, int, str], tuple[float, str]] = {}
    with RESULTS_PATH.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = (
                row["kind"],
                row["dataset_type"],
                int(row["size"]),
                row["scenario"],
            )
            average_time = float(row["average_time_seconds"])
            if key not in best_rows or average_time < best_rows[key][0]:
                best_rows[key] = (average_time, row["algorithm"])

    return {key: value[1] for key, value in best_rows.items()}
