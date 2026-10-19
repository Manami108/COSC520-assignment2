# COSC 520 Assignment 2 — Advanced Data Structures

Comparison of three binary search trees implemented in Python: **AVL Tree, Treap, and Scapegoat Tree**.

The project compares their performance and examines how different balancing strategies respond to insertion order and deletion.

## Implementations

Each tree supports:

- `insert(key)` — add a key (returns `False` for duplicates)
- `search(key)` — return whether a key exists
- `delete(key)` — remove a key (returns `False` if absent)

Additional methods: `inorder()`, `height()`, and `storage_bytes()`.

## Project Structure

```text
structures/         AVL, Treap, Scapegoat, and shared BST code
tests/
  tests.py          Unit tests
experiments/
  dataset.py        Dataset generation
  benchmark.py      Performance experiments
  plot.py           Combined comparison figures
  demo.py           Basic demonstration
data/               Generated binary datasets
results/            CSV results and figures
```

## Requirements

- Python 3.12+
- Matplotlib (plots only)

```bash
python -m pip install matplotlib
```

Run all commands from the project root.

## How to Run

### 1. Unit tests

```bash
python -m unittest tests.tests -v
```

### 2. Demonstration

```bash
python -m experiments.demo
```

### 3. Generate datasets (optional)

```bash
python -m experiments.dataset --sizes 10000 100000 1000000 --order random
```

Datasets contain unique, even 64-bit integer keys. Use `--order ascending` or `--order descending` for other input orders. The benchmark also generates missing datasets automatically.

### 4. Run benchmarks

Run the same dataset sizes for each insertion order:

```bash
python -m experiments.benchmark --sizes 10000 100000 1000000 --order random --repeats 3 --shrink
python -m experiments.benchmark --sizes 10000 100000 1000000 --order ascending --repeats 3
python -m experiments.benchmark --sizes 10000 100000 1000000 --order descending --repeats 3
```

`--shrink` is optional. It measures the average time to delete 60% of the original keys and records the resulting tree height. For larger datasets, adjust sizes according to available memory and runtime.

### 5. Generate plots

```bash
python -m experiments.plot --order all
```

This generates two combined figures:

- `results/figures/summary_random.png` — build, search, insertion, and deletion times; tree height; average successful-search depth.
- `results/figures/insertion_order.png` — build time and tree height for random, ascending, and descending insertion at the largest dataset size common to all three results files.

## Evaluation

| Experiment | Measurements | Purpose |
|---|---|---|
| Performance and scaling | Build, search, insertion, deletion, memory | Compare cost as the number of keys increases |
| Tree structure | Height, average successful-search depth | Relate balancing to search performance |
| Insertion order | Random, ascending, descending | Examine sensitivity to input ordering |
| Large-scale deletion (optional) | Average deletion time and height after 60% removal | Examine behavior after substantial deletion |

The search benchmark uses 50% existing keys and 50% absent keys. Timing results are reported per operation except for total build time. Memory refers to allocated tree-array storage, not total process memory.

Results are saved in `results/bench_random.csv`, `results/bench_ascending.csv`, and `results/bench_descending.csv`. Each benchmark run overwrites the CSV for its insertion order.
