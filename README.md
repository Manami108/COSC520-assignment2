# COSC 520 Assignment 2 — Advanced Data Structures

Comparison of three binary search trees implemented in Python: **AVL Tree, Treap, and Scapegoat Tree**.

The experiments compare running time, tree height, average search depth, and memory usage across different dataset sizes and insertion orders.

## Project Structure

```text
structures/         AVL, Treap, Scapegoat, and shared BST code
experiments/
  dataset.py        Generate datasets
  benchmark.py      Run performance experiments
  plot.py           Generate figures and a summary table
  demo.py           Basic demonstration
tests/
  tests.py          Unit tests
data/               Generated datasets
results/            Benchmark CSVs, summary table, and figures
```

## Requirements

- Python 3.12+
- Matplotlib (for plotting)

```bash
python3 -m pip install matplotlib
```

Run all commands **from the project root**.

## How to Run

### 1. Unit Tests

```bash
python3 -m unittest tests.tests -v
```

### 2. Demonstration

```bash
python3 -m experiments.demo
```

### 3. Run Benchmarks

Dataset sizes and experiment settings are defined in the code. **Only insertion order needs to be selected.**

**Random insertion (default):**

```bash
python3 -m experiments.benchmark
```

**Ascending insertion:**

```bash
python3 -m experiments.benchmark --order ascending
```

**Descending insertion:**

```bash
python3 -m experiments.benchmark --order descending
```

**All three insertion orders:**

```bash
python3 -m experiments.benchmark --order all
```

Datasets are generated automatically and reused when an existing file has the expected size. There is no need to run `dataset.py` separately.

### 4. Generate Plots and Summary Table

After running the benchmarks:

```bash
python3 -m experiments.plot
```

This generates figures for every insertion order with an available benchmark CSV, along with a median-results table. To plot only one insertion order:

```bash
python3 -m experiments.plot --order random
```

No bar charts are generated. The former insertion-order bar chart has been replaced by a CSV summary that can be used to create tables for the report.

## Experiment Settings

The following sizes and settings are fixed in the Python files and do not need command-line arguments.

In `experiments/dataset.py`:

```python
SIZES = (100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000)
SEED = 42
```

In `experiments/benchmark.py`:

```python
REPEATS = 3
QUERIES = 3_000
UPDATES = 1_000
SHRINK = True
```

Each dataset contains distinct even-numbered 64-bit integers. Random, ascending, and descending datasets contain the same keys, differing in insertion order. The random dataset uses a fixed seed; the three repetitions reuse its insertion order but vary the sampled queries and Treap random seed.

For a smaller trial run, temporarily edit `SIZES` in `dataset.py`, then restore the full list before final benchmarking. The 10-million-key experiments may require substantial memory and execution time.

## Evaluation

| Experiment | Measurements |
|---|---|
| Performance and scaling | Build time, successful and unsuccessful search, insertion, deletion |
| Tree structure | Height, average successful-search depth, allocated tree-array storage |
| Insertion order | Random, ascending, descending |
| Bulk deletion | Average time to remove 60% of original keys and resulting tree height |

- **Build time:** Time required to insert all original keys, measured in seconds.
- **Search:** Average time per successful or unsuccessful query, measured in microseconds. Unsuccessful searches use absent odd-numbered keys.
- **Insertion and deletion:** Average time per operation for up to 1,000 temporary odd-numbered keys. The ordinary deletion test removes those newly inserted keys.
- **Bulk deletion:** Removes 60% of the original keys, spread across the key range and deleted in increasing-key order. This is not a random-deletion workload.
- **Tree structure:** Height, average successful-search depth, and storage are measured immediately after the initial build, before the update experiments.
- **Memory:** Reports allocated tree-array storage (`tree.storage_bytes()`), not total Python process memory.

Each measurement is repeated three times. The plot values and summary table use the **median** of those repetitions.

## Figures

The plotting script generates two figures per insertion order:

1. **Timing (`times_*.png`):** Build time, successful search, unsuccessful search, insertion, deletion, and 60% bulk deletion.
2. **Structure (`structure_*.png`):** Tree height, average successful-search depth, and allocated array storage.

The tree colors are consistent across all plots: **red for AVL, blue for Treap, and green for Scapegoat**. Dataset size uses a logarithmic x-axis. Build time and storage also use logarithmic y-axes.

The height plot includes a gray dashed `log₂(n + 1)` reference curve to help visualize logarithmic height growth; it is not a fourth algorithm or measured result.

## Results

Raw benchmark results are saved as:

```text
results/
  bench_random.csv
  bench_ascending.csv
  bench_descending.csv
  summary.csv
```

Each `bench_*.csv` file records individual repetitions. `summary.csv` contains median values grouped by insertion order, tree, and dataset size.

Figures are saved as:

```text
results/figures/
  times_random.png
  structure_random.png
  times_ascending.png
  structure_ascending.png
  times_descending.png
  structure_descending.png
```

Only files for completed insertion orders are created. Running the benchmark again for an insertion order **overwrites that order's existing CSV**. Running the plot script again **overwrites `summary.csv`** with the data for the insertion orders selected in that plotting run.
