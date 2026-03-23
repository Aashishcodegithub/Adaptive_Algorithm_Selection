from __future__ import annotations

import csv
import json
import random
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Iterable

from adaptive_selector import recommend_search_algorithm, recommend_sort_algorithm
from algorithms.searching import SEARCHING_ALGORITHMS
from algorithms.sorting import SORTING_ALGORITHMS

DEFAULT_SIZES = (100, 1000, 5000, 10000)
DEFAULT_TRIALS = 5
SORTING_DATASET_TYPES = ("random", "sorted", "reverse", "nearly_sorted", "few_unique")
SEARCH_TARGET_MODES = ("front", "middle", "end", "missing")
DEFAULT_DASHBOARD_DATA_PATH = Path("docs/results-data.js")


@dataclass(frozen=True)
class BenchmarkRow:
    kind: str
    dataset_type: str
    size: int
    scenario: str
    algorithm: str
    average_time_seconds: float
    recommended_algorithm: str


@dataclass(frozen=True)
class BenchmarkSummary:
    fastest_counts: dict[str, Counter]
    recommendation_hits: dict[str, int]
    scenario_totals: dict[str, int]


def generate_sorting_dataset(
    size: int, dataset_type: str, rng: random.Random
) -> list[int]:
    values = [rng.randint(1, 10_000) for _ in range(size)]

    if dataset_type == "random":
        return values
    if dataset_type == "sorted":
        return sorted(values)
    if dataset_type == "reverse":
        return sorted(values, reverse=True)
    if dataset_type == "nearly_sorted":
        values = sorted(values)
        swap_count = max(1, size // 10)
        for _ in range(swap_count):
            left = rng.randrange(size)
            right = rng.randrange(size)
            values[left], values[right] = values[right], values[left]
        return values
    if dataset_type == "few_unique":
        return [rng.randint(1, 10) for _ in range(size)]

    raise ValueError(f"Unsupported dataset type: {dataset_type}")


def build_search_dataset(size: int, rng: random.Random) -> list[int]:
    return sorted(generate_sorting_dataset(size, "random", rng))


def choose_target(dataset: list[int], mode: str) -> int:
    if mode == "front":
        return dataset[0]
    if mode == "middle":
        return dataset[len(dataset) // 2]
    if mode == "end":
        return dataset[-1]
    if mode == "missing":
        return max(dataset) + 1 if dataset else 1

    raise ValueError(f"Unsupported search scenario: {mode}")


def run_sorting_benchmarks(
    *,
    sizes: Iterable[int] = DEFAULT_SIZES,
    dataset_types: Iterable[str] = SORTING_DATASET_TYPES,
    trials: int = DEFAULT_TRIALS,
    seed: int = 42,
    bubble_limit: int = 2_000,
) -> list[BenchmarkRow]:
    rng = random.Random(seed)
    rows: list[BenchmarkRow] = []

    for dataset_type in dataset_types:
        for size in sizes:
            dataset = generate_sorting_dataset(size, dataset_type, rng)
            expected = sorted(dataset)
            recommendation = recommend_sort_algorithm(dataset)

            for key, algorithm in SORTING_ALGORITHMS.items():
                if key == "bubble" and size > bubble_limit:
                    continue

                total_time = 0.0
                for _ in range(trials):
                    trial_input = list(dataset)
                    start = perf_counter()
                    result = algorithm(trial_input)
                    total_time += perf_counter() - start

                if result != expected:
                    raise ValueError(f"{key} produced an incorrect sorting result.")

                rows.append(
                    BenchmarkRow(
                        kind="sorting",
                        dataset_type=dataset_type,
                        size=size,
                        scenario="-",
                        algorithm=key,
                        average_time_seconds=total_time / trials,
                        recommended_algorithm=recommendation.algorithm_key,
                    )
                )

    return rows


def run_searching_benchmarks(
    *,
    sizes: Iterable[int] = DEFAULT_SIZES,
    target_modes: Iterable[str] = SEARCH_TARGET_MODES,
    trials: int = DEFAULT_TRIALS,
    seed: int = 42,
    repeat_count: int = 1_000,
) -> list[BenchmarkRow]:
    rng = random.Random(seed + 1)
    rows: list[BenchmarkRow] = []

    for size in sizes:
        dataset = build_search_dataset(size, rng)

        for target_mode in target_modes:
            target = choose_target(dataset, target_mode)
            recommendation = recommend_search_algorithm(
                dataset,
                assume_sorted=True,
                target_position_hint=target_mode,
            )

            for key, algorithm in SEARCHING_ALGORITHMS.items():
                total_time = 0.0
                for _ in range(trials):
                    start = perf_counter()
                    result = -1
                    for _ in range(repeat_count):
                        result = algorithm(dataset, target)
                    total_time += perf_counter() - start

                if target_mode == "missing":
                    if result != -1:
                        raise ValueError(f"{key} should not find a missing target.")
                elif result == -1 or dataset[result] != target:
                    raise ValueError(f"{key} returned an invalid index.")

                rows.append(
                    BenchmarkRow(
                        kind="searching",
                        dataset_type="sorted",
                        size=size,
                        scenario=target_mode,
                        algorithm=key,
                        average_time_seconds=(total_time / trials) / repeat_count,
                        recommended_algorithm=recommendation.algorithm_key,
                    )
                )

    return rows


def run_benchmarks(
    *,
    kind: str = "all",
    sizes: Iterable[int] = DEFAULT_SIZES,
    trials: int = DEFAULT_TRIALS,
    seed: int = 42,
) -> list[BenchmarkRow]:
    rows: list[BenchmarkRow] = []

    if kind in {"sorting", "all"}:
        rows.extend(run_sorting_benchmarks(sizes=sizes, trials=trials, seed=seed))
    if kind in {"searching", "all"}:
        rows.extend(run_searching_benchmarks(sizes=sizes, trials=trials, seed=seed))

    return rows


def write_results_csv(rows: Iterable[BenchmarkRow], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "kind",
                "dataset_type",
                "size",
                "scenario",
                "algorithm",
                "average_time_seconds",
                "recommended_algorithm",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_dashboard_data_js(
    rows: Iterable[BenchmarkRow], output_path: str | Path = DEFAULT_DASHBOARD_DATA_PATH
) -> None:
    row_list = list(rows)
    summary = summarize_benchmarks(row_list)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "rows": [asdict(row) for row in row_list],
        "summary": {
            "fastest_counts": {
                kind: dict(counter) for kind, counter in summary.fastest_counts.items()
            },
            "recommendation_hits": dict(summary.recommendation_hits),
            "scenario_totals": dict(summary.scenario_totals),
        },
        "cases": build_case_summaries(row_list),
    }

    with path.open("w", encoding="utf-8") as handle:
        handle.write("window.BENCHMARK_DASHBOARD_DATA = ")
        json.dump(payload, handle, indent=2)
        handle.write(";\n")


def build_case_summaries(rows: Iterable[BenchmarkRow]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, int, str], list[BenchmarkRow]] = defaultdict(list)

    for row in rows:
        grouped[(row.kind, row.dataset_type, row.size, row.scenario)].append(row)

    cases: list[dict[str, object]] = []
    for key, group in sorted(grouped.items()):
        fastest = min(group, key=lambda item: item.average_time_seconds)
        recommendation = group[0].recommended_algorithm
        cases.append(
            {
                "kind": key[0],
                "dataset_type": key[1],
                "size": key[2],
                "scenario": key[3],
                "fastest_algorithm": fastest.algorithm,
                "fastest_time_seconds": fastest.average_time_seconds,
                "recommended_algorithm": recommendation,
                "recommendation_hit": recommendation == fastest.algorithm,
            }
        )

    return cases


def summarize_benchmarks(rows: Iterable[BenchmarkRow]) -> BenchmarkSummary:
    grouped: dict[tuple[str, str, int, str], list[BenchmarkRow]] = defaultdict(list)

    for row in rows:
        key = (row.kind, row.dataset_type, row.size, row.scenario)
        grouped[key].append(row)

    fastest_counts: dict[str, Counter] = {"sorting": Counter(), "searching": Counter()}
    recommendation_hits = {"sorting": 0, "searching": 0}
    scenario_totals = {"sorting": 0, "searching": 0}

    for key, group in grouped.items():
        kind = key[0]
        fastest = min(group, key=lambda item: item.average_time_seconds)
        fastest_counts[kind][fastest.algorithm] += 1
        scenario_totals[kind] += 1

        if group[0].recommended_algorithm == fastest.algorithm:
            recommendation_hits[kind] += 1

    return BenchmarkSummary(
        fastest_counts=fastest_counts,
        recommendation_hits=recommendation_hits,
        scenario_totals=scenario_totals,
    )
