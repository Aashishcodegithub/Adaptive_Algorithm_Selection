from __future__ import annotations

import unittest

from adaptive_selector import recommend_search_algorithm, recommend_sort_algorithm


class SelectorTests(unittest.TestCase):
    def test_small_dataset_prefers_insertion_sort(self) -> None:
        recommendation = recommend_sort_algorithm([3, 1, 2, 4, 5])
        self.assertEqual(recommendation.algorithm_key, "insertion")

    def test_duplicate_heavy_large_dataset_prefers_heap_sort(self) -> None:
        data = ([1, 2, 3, 4, 5] * 1000)
        recommendation = recommend_sort_algorithm(data)
        self.assertEqual(recommendation.algorithm_key, "heap")

    def test_unsorted_search_prefers_linear_search(self) -> None:
        recommendation = recommend_search_algorithm([4, 1, 3, 2])
        self.assertEqual(recommendation.algorithm_key, "linear")

    def test_front_loaded_sorted_search_prefers_exponential_search(self) -> None:
        recommendation = recommend_search_algorithm(
            list(range(1000)),
            assume_sorted=True,
            target_position_hint="front",
        )
        self.assertEqual(recommendation.algorithm_key, "exponential")
