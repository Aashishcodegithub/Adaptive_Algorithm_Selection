from __future__ import annotations

import math
from collections import OrderedDict
from typing import Sequence


def linear_search(values: Sequence[int], target: int) -> int:
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


def binary_search(values: Sequence[int], target: int) -> int:
    return _binary_search_range(values, target, 0, len(values) - 1)


def jump_search(values: Sequence[int], target: int) -> int:
    n = len(values)
    if n == 0:
        return -1

    step = max(1, int(math.sqrt(n)))
    prev = 0

    while prev < n and values[min(step, n) - 1] < target:
        prev = step
        step += max(1, int(math.sqrt(n)))
        if prev >= n:
            return -1

    while prev < min(step, n) and values[prev] < target:
        prev += 1

    if prev < n and values[prev] == target:
        return prev

    return -1


def exponential_search(values: Sequence[int], target: int) -> int:
    n = len(values)
    if n == 0:
        return -1
    if values[0] == target:
        return 0

    bound = 1
    while bound < n and values[bound] < target:
        bound *= 2

    left = bound // 2
    right = min(bound, n - 1)
    return _binary_search_range(values, target, left, right)


def _binary_search_range(
    values: Sequence[int], target: int, left: int, right: int
) -> int:
    while left <= right:
        mid = (left + right) // 2
        if values[mid] == target:
            return mid
        if values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


SEARCHING_ALGORITHMS = OrderedDict(
    [
        ("linear", linear_search),
        ("binary", binary_search),
        ("jump", jump_search),
        ("exponential", exponential_search),
    ]
)

SEARCHING_LABELS = {
    "linear": "Linear Search",
    "binary": "Binary Search",
    "jump": "Jump Search",
    "exponential": "Exponential Search",
}
