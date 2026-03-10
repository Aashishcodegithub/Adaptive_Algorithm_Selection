import time
import random
import csv

from algorithms.sorting import bubble_sort, merge_sort, quick_sort, heap_sort


# Algorithms dictionary
algorithms = {
    "Bubble Sort": bubble_sort,
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort,
    "Heap Sort": heap_sort
}


# Dataset sizes to test
sizes = [100, 1000, 5000, 10000]


# Number of times each algorithm runs (to average time)
trials = 5


# Dataset generators
def generate_dataset(size, dataset_type):

    arr = [random.randint(1,10000) for _ in range(size)]

    if dataset_type == "random":
        return arr

    elif dataset_type == "sorted":
        return sorted(arr)

    elif dataset_type == "reverse":
        return sorted(arr, reverse=True)

    elif dataset_type == "nearly_sorted":
        arr = sorted(arr)
        for _ in range(int(size * 0.1)):
            i = random.randint(0,size-1)
            j = random.randint(0,size-1)
            arr[i],arr[j] = arr[j],arr[i]
        return arr


dataset_types = ["random","sorted","reverse","nearly_sorted"]


# Store results
results = {}


# CSV file for ML dataset
with open("results.csv","w",newline="") as file:

    writer = csv.writer(file)
    writer.writerow(["dataset_type","size","algorithm","time"])


    for dataset_type in dataset_types:

        print(f"\nDataset Type: {dataset_type}")

        results[dataset_type] = {}

        for size in sizes:

            arr = generate_dataset(size,dataset_type)

            results[dataset_type][size] = {}

            print(f"\nDataset Size: {size}")

            for name,algo in algorithms.items():

                if name == "Bubble Sort" and size > 2000:
                    print(f"{name} : Skipped (too slow)")
                    continue
                total_time=0
                for _ in range(trials):

                    data = arr.copy()

                    start = time.time()

                    algo(data)

                    end = time.time()

                    total_time += (end-start)


                avg_time = total_time / trials

                results[dataset_type][size][name] = avg_time

                writer.writerow([dataset_type,size,name,avg_time])

                print(f"{name} : {avg_time:.6f} seconds")


            best = min(results[dataset_type][size], key=results[dataset_type][size].get)

            print(f"Best Algorithm → {best}")