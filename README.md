# Adaptive Algorithm Selection Project

This project benchmarks classic sorting and searching algorithms, profiles the input data, and recommends an algorithm that fits the workload. When `results.csv` is available, the selector uses those measured winners first and falls back to heuristics otherwise.

## What is included

- Correct implementations of bubble, insertion, merge, quick, and heap sort.
- Correct implementations of linear, binary, jump, and exponential search.
- An adaptive selector that recommends algorithms from dataset characteristics.
- A CLI for sorting, searching, and benchmark generation.
- A static dashboard in `docs/` for presenting benchmark results visually.
- Automated tests using the Python standard library.

## Usage

Run a full benchmark and write the results to `results.csv`:

```bash
python3 __main__.py benchmark
```

That command also updates `docs/results-data.js`, which powers the frontend dashboard.

Sort with automatic algorithm selection:

```bash
python3 __main__.py sort --data 5,1,4,2,8
```

Search with automatic algorithm selection:

```bash
python3 __main__.py search --data 1,3,5,7,9 --target 7 --assume-sorted
```

Select a specific algorithm manually:

```bash
python3 __main__.py sort --data 5,1,4,2,8 --algorithm merge
python3 __main__.py search --data 1,3,5,7,9 --target 7 --algorithm binary --assume-sorted
```

## Running tests

```bash
python3 -m unittest discover -s tests -v
```

## Frontend dashboard

Open `docs/index.html` in a browser for a local view, or serve the repository with:

```bash
python3 -m http.server
```

If you enable GitHub Pages for the `docs/` folder on `main`, the same dashboard will work as a hosted site.

## Benchmark output

The generated CSV contains:

- `kind`: `sorting` or `searching`
- `dataset_type`: input distribution
- `size`: dataset size
- `scenario`: search scenario or `-` for sorting
- `algorithm`: algorithm that was timed
- `average_time_seconds`: average runtime across trials
- `recommended_algorithm`: selector output for that scenario
