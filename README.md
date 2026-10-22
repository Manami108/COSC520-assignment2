# COSC 520 Assignment 2 — Advanced Data Structures

Comparison of three binary search trees implemented in Python: **AVL Tree, Treap, and Scapegoat Tree**.

The experiments compare running time, tree height, search depth, and memory usage across different dataset sizes and insertion orders.

## Project Structure

```text
structures/         AVL, Treap, Scapegoat, shared BST code
experiments/
  dataset.py        Generate datasets
  benchmark.py      Run performance experiments
  plot.py           Generate figures
  demo.py           Basic demonstration
tests/
  tests.py          Unit tests
data/               Generated datasets
results/            Benchmark CSVs and figures
```

## Requirements

- Python 3.12+
- Matplotlib (for plotting)

```bash
python -m pip install matplotlib
```

Run all commands from the project root.

## How to Run

### 1. Unit Tests

```bash
python -m unittest tests.tests -v
```

### 2. Demonstration

```bash
python -m experiments.demo
```

### 3. Small Test Run

Before running large datasets, check that the benchmark and plotting code work.

```bash
python -m experiments.benchmark --sizes 10000 100000 --order random --repeats 3 --shrink --tag pilot

python -m experiments.plot --order random --tag pilot
```

### 4. Full Benchmarks

The final experiments use **10K, 100K, 1M, and 10M keys**, with three repetitions for each insertion order.

**Random insertion**

```bash
python -m experiments.benchmark --sizes 10000 100000 1000000 10000000 --order random --repeats 3 --shrink --tag final
```

**Ascending insertion**

```bash
python -m experiments.benchmark --sizes 10000 100000 1000000 10000000 --order ascending --repeats 3 --shrink --tag final
```

**Descending insertion**

```bash
python -m experiments.benchmark --sizes 10000 100000 1000000 10000000 --order descending --repeats 3 --shrink --tag final
```

Datasets are generated automatically if they do not already exist.

The 10-million-key experiments can require substantial memory and processing time. If necessary, first run the experiments without `10000000`.

### 5. Generate Final Plots

After completing the benchmarks:

```bash
python -m experiments.plot --order random --tag final
python -m experiments.plot --order ascending --tag final
python -m experiments.plot --order descending --tag final
python -m experiments.plot --order all --tag final
```

The last command creates the insertion-order comparison using the largest dataset size shared across random, ascending, and descending results.

## Evaluation

| Experiment | Measurements |
|---|---|
| Performance and scaling | Build time, successful and unsuccessful search, insertion and deletion |
| Tree structure | Height, average search depth, allocated array storage |
| Insertion order | Random, ascending and descending |
| Bulk deletion | Average time to delete 60% of original keys and resulting height |

The datasets contain unique even-numbered 64-bit integers. Odd-numbered keys are used for unsuccessful searches and temporary insertion experiments.

Bulk deletion removes keys distributed across the original value range in increasing-key order. It is not a random-deletion workload.

Build time is measured in seconds. Individual search, insertion, and deletion times are reported in microseconds per operation. Memory measures allocated tree-array storage rather than total process memory.

The plots use the median of three repetitions.

## Results

Benchmark CSVs are saved in:

```text
results/
  bench_random_final.csv
  bench_ascending_final.csv
  bench_descending_final.csv
```

Generated figures are saved in:

```text
results/figures/
  times_random_final.png
  structure_random_final.png
  times_ascending_final.png
  structure_ascending_final.png
  times_descending_final.png
  structure_descending_final.png
  insertion_order_final.png
```

The `--tag` option identifies each experiment. For example, `--tag pilot` generates separate pilot results, while `--tag final` generates final results.

**Note:** Running a benchmark again with the same insertion order and tag will overwrite its existing CSV file.

## Submission

The final PDF report should include:

- Explanation and applications of AVL, Treap, and Scapegoat trees
- Theoretical time and space complexity analysis
- Performance tables and plots
- Discussion of the experimental results
- GitHub repository link
- Dataset link
- References and any required AI-use disclosure

