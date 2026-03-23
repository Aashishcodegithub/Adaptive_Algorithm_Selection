from __future__ import annotations

import unittest

from algorithms.searching import SEARCHING_ALGORITHMS
from algorithms.sorting import SORTING_ALGORITHMS


class SortingAlgorithmTests(unittest.TestCase):
    def test_all_sorting_algorithms_return_sorted_copy(self) -> None:
        data = [9, 1, 5, 3, 5, -2, 8]
        expected = sorted(data)

        for name, algorithm in SORTING_ALGORITHMS.items():
            with self.subTest(algorithm=name):
                original = list(data)
                self.assertEqual(algorithm(data), expected)
                self.assertEqual(data, original)


class SearchingAlgorithmTests(unittest.TestCase):
    def test_all_searching_algorithms_find_existing_targets(self) -> None:
        data = [1, 3, 5, 7, 9, 11, 13, 15]

        for name, algorithm in SEARCHING_ALGORITHMS.items():
            with self.subTest(algorithm=name):
                index = algorithm(data, 11)
                self.assertNotEqual(index, -1)
                self.assertEqual(data[index], 11)

    def test_all_searching_algorithms_return_negative_one_for_missing_targets(self) -> None:
        data = [2, 4, 6, 8, 10, 12]

        for name, algorithm in SEARCHING_ALGORITHMS.items():
            with self.subTest(algorithm=name):
                self.assertEqual(algorithm(data, 5), -1)

    def test_searching_algorithms_handle_empty_input(self) -> None:
        for name, algorithm in SEARCHING_ALGORITHMS.items():
            with self.subTest(algorithm=name):
                self.assertEqual(algorithm([], 1), -1)
