from __future__ import annotations

import heapq
from collections import OrderedDict
from typing import Iterable


def bubble_sort(values: Iterable[int]) -> list[int]:
    arr = list(values)
    n = len(arr)

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        if not swapped:
            break

    return arr


def insertion_sort(values: Iterable[int]) -> list[int]:
    arr = list(values)

    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key

    return arr


def merge_sort(values: Iterable[int]) -> list[int]:
    arr = list(values)

    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    merged: list[int] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged


def quick_sort(values: Iterable[int]) -> list[int]:
    arr = list(values)

    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    left = [value for value in arr if value < pivot]
    middle = [value for value in arr if value == pivot]
    right = [value for value in arr if value > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def heap_sort(values: Iterable[int]) -> list[int]:
    heap = list(values)
    heapq.heapify(heap)
    return [heapq.heappop(heap) for _ in range(len(heap))]


SORTING_ALGORITHMS = OrderedDict(
    [
        ("bubble", bubble_sort),
        ("insertion", insertion_sort),
        ("merge", merge_sort),
        ("quick", quick_sort),
        ("heap", heap_sort),
    ]
)

SORTING_LABELS = {
    "bubble": "Bubble Sort",
    "insertion": "Insertion Sort",
    "merge": "Merge Sort",
    "quick": "Quick Sort",
    "heap": "Heap Sort",
}
