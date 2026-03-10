import math

def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid

        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1

def jump_search(arr, target):
    n = len(arr)
    step = int(math.sqrt(n))
    prev = 0

    while arr[min(step, n)-1] < target:
        prev = step
        step += int(math.sqrt(n))

        if prev >= n:
            return -1

    while arr[prev] < target:
        prev += 1

        if prev == min(step, n):
            return -1

    if arr[prev] == target:
        return prev

    return -1

def exponential_search(arr, target):
    if arr[0] == target:
        return 0

    n = len(arr)
    i = 1

    while i < n and arr[i] <= target:
        i *= 2

    return binary_search(arr[:min(i,n)], target)

