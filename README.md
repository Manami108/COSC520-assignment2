# COSC 520 Assignment 2 — Advanced Data Structures

Comparison of three self-implemented Binary Search Trees: **AVL Tree, Treap, and Scapegoat Tree**.

## Implementations

All three trees support:
- `insert(key)` — insert a key
- `search(key)` — check whether a key exists
- `delete(key)` — remove a key

Additional methods: `inorder()`, `height()`, and `storage_bytes()`.

## Project Structure

```text
structures/     Tree implementations
tests/          Unit tests
experiments/
  dataset.py    Dataset generation
  benchmark.py  Performance evaluation
  plot.py       Visualization
  demo.py       Basic demonstration
data/           Generated datasets
results/        Benchmark results and plots
```

## Requirements

- Python 3.12+
- Matplotlib (for plots)

```bash
python -m pip install matplotlib
```

## How to Run

Run all commands from the project root.

**1. Unit tests**
```bash
python -m unittest tests.tests -v
```

**2. Demonstration**
```bash
python -m experiments.demo
```

**3. Generate datasets**
```bash
python -m experiments.dataset --sizes 10000 100000 1000000
```

**4. Run benchmarks**
```bash
python -m experiments.benchmark --sizes 10000 100000 1000000 --repeats 3
```

**5. Generate plots**
```bash
python -m experiments.plot
```

Use `--order ascending` or `--order descending` for other insertion orders in both dataset generation and benchmarking.

## Evaluation

- Dataset sizes: 10K, 100K, 1M (target: 10M)
- Insertion orders: random, ascending, descending
- Metrics: build time, search time, insertion time, deletion time, tree height, and array storage

Results are saved as CSV files and PNG figures in `results/`.

## AI Usage

AI tools assisted with code development, debugging, and documentation. All implementations and experimental results should be independently reviewed and verified before submission.
