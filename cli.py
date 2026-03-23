from __future__ import annotations

import argparse
from typing import Sequence

from adaptive_selector import (
    is_non_decreasing,
    recommend_search_algorithm,
    recommend_sort_algorithm,
)
from algorithms.searching import SEARCHING_ALGORITHMS, SEARCHING_LABELS
from algorithms.sorting import SORTING_ALGORITHMS, SORTING_LABELS
from benchmark import (
    DEFAULT_DASHBOARD_DATA_PATH,
    DEFAULT_SIZES,
    DEFAULT_TRIALS,
    run_benchmarks,
    summarize_benchmarks,
    write_dashboard_data_js,
    write_results_csv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Adaptive algorithm selection for sorting and searching problems."
    )
    subparsers = parser.add_subparsers(dest="command")

    benchmark_parser = subparsers.add_parser(
        "benchmark", help="Benchmark all implemented algorithms and export CSV results."
    )
    benchmark_parser.add_argument(
        "--kind",
        choices=("sorting", "searching", "all"),
        default="all",
        help="Select which benchmark suite to run.",
    )
    benchmark_parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=list(DEFAULT_SIZES),
        help="Dataset sizes to benchmark.",
    )
    benchmark_parser.add_argument(
        "--trials",
        type=int,
        default=DEFAULT_TRIALS,
        help="How many times to run each benchmark case.",
    )
    benchmark_parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used for repeatable dataset generation.",
    )
    benchmark_parser.add_argument(
        "--output",
        default="results.csv",
        help="Path to the CSV file that will store benchmark results.",
    )
    benchmark_parser.add_argument(
        "--dashboard-output",
        default=str(DEFAULT_DASHBOARD_DATA_PATH),
        help="Path to the generated frontend data file.",
    )
    benchmark_parser.set_defaults(handler=handle_benchmark)

    sort_parser = subparsers.add_parser(
        "sort", help="Sort a dataset using a selected algorithm or the adaptive selector."
    )
    sort_parser.add_argument(
        "--data",
        required=True,
        help="Comma-separated integers to sort, for example: 5,1,4,2,8",
    )
    sort_parser.add_argument(
        "--algorithm",
        choices=("auto", *SORTING_ALGORITHMS.keys()),
        default="auto",
        help="Sorting algorithm to use.",
    )
    sort_parser.set_defaults(handler=handle_sort)

    search_parser = subparsers.add_parser(
        "search", help="Search for a target using a selected algorithm or the adaptive selector."
    )
    search_parser.add_argument(
        "--data",
        required=True,
        help="Comma-separated integers to search inside.",
    )
    search_parser.add_argument(
        "--target",
        required=True,
        type=int,
        help="Target integer to search for.",
    )
    search_parser.add_argument(
        "--algorithm",
        choices=("auto", *SEARCHING_ALGORITHMS.keys()),
        default="auto",
        help="Search algorithm to use.",
    )
    search_parser.add_argument(
        "--assume-sorted",
        action="store_true",
        help="Skip sortedness detection and treat the input as sorted.",
    )
    search_parser.add_argument(
        "--repeated-queries",
        action="store_true",
        help="Hint that the same dataset will be searched repeatedly.",
    )
    search_parser.add_argument(
        "--target-position-hint",
        choices=("front", "middle", "end", "unknown"),
        default="unknown",
        help="Hint about where the target is likely to appear in a sorted dataset.",
    )
    search_parser.set_defaults(handler=handle_search)

    return parser


def parse_int_list(raw: str) -> list[int]:
    values = [chunk.strip() for chunk in raw.split(",")]
    if not values or any(value == "" for value in values):
        raise ValueError("Input data must be a comma-separated list of integers.")
    return [int(value) for value in values]


def handle_benchmark(args: argparse.Namespace) -> int:
    rows = run_benchmarks(kind=args.kind, sizes=args.sizes, trials=args.trials, seed=args.seed)
    write_results_csv(rows, args.output)
    write_dashboard_data_js(rows, args.dashboard_output)
    summary = summarize_benchmarks(rows)

    print(f"Benchmarked {len(rows)} runs and wrote results to {args.output}.")
    print(f"Dashboard data written to {args.dashboard_output}.")
    for kind in ("sorting", "searching"):
        if summary.scenario_totals[kind] == 0:
            continue

        hits = summary.recommendation_hits[kind]
        total = summary.scenario_totals[kind]
        winners = ", ".join(
            f"{algorithm}={count}"
            for algorithm, count in summary.fastest_counts[kind].most_common()
        )
        print(f"{kind.title()} recommendation hit rate: {hits}/{total}")
        print(f"{kind.title()} empirical winners: {winners}")

    return 0


def handle_sort(args: argparse.Namespace) -> int:
    data = parse_int_list(args.data)

    if args.algorithm == "auto":
        recommendation = recommend_sort_algorithm(data)
        algorithm_key = recommendation.algorithm_key
        print(f"Recommended: {recommendation.label}")
        print(f"Reason: {recommendation.rationale}")
    else:
        algorithm_key = args.algorithm
        print(f"Selected: {SORTING_LABELS[algorithm_key]}")

    result = SORTING_ALGORITHMS[algorithm_key](data)
    print(f"Sorted data: {result}")
    return 0


def handle_search(args: argparse.Namespace) -> int:
    data = parse_int_list(args.data)
    assume_sorted = args.assume_sorted or None

    if args.algorithm == "auto":
        recommendation = recommend_search_algorithm(
            data,
            assume_sorted=assume_sorted,
            repeated_queries=args.repeated_queries,
            target_position_hint=args.target_position_hint,
        )
        algorithm_key = recommendation.algorithm_key
        print(f"Recommended: {recommendation.label}")
        print(f"Reason: {recommendation.rationale}")
    else:
        algorithm_key = args.algorithm
        print(f"Selected: {SEARCHING_LABELS[algorithm_key]}")

    if algorithm_key != "linear" and not (args.assume_sorted or is_non_decreasing(data)):
        raise SystemExit("Binary, jump, and exponential search require sorted input.")

    index = SEARCHING_ALGORITHMS[algorithm_key](data, args.target)
    if index == -1:
        print(f"Target {args.target} was not found.")
    else:
        print(f"Target {args.target} found at index {index}.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "handler"):
        parser.print_help()
        return 0

    try:
        return args.handler(args)
    except ValueError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    raise SystemExit(main())
