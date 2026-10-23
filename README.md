# COSC 520 Assignment 2 

Hi! Welcome back to my GitHub repository <3

This repository contains the implementation and experimental comparison of three self-balancing binary search trees (**AVL Tree**, **Treap**, and **Scapegoat Tree**).

All algorithms and data structures were implemented from scratch in Python. The experiments compare performance in execution time, tree height, and memory usage across different dataset sizes and insertion orders.

## Repository Structure

```text
COSC520-assignment2/
│
├── structures/
│   ├── __init__.py
│   ├── base.py
│   ├── avl.py
│   ├── treap.py
│   └── scapegoat.py
│
├── experiments/
│   ├── __init__.py
│   ├── dataset.py
│   ├── benchmark.py
│   ├── plot.py
│   └── demo.py
│
├── tests/
│   ├── __init__.py
│   └── tests.py
│
├── data/
├── results/
└── README.md
```
## Implementations

The three binary search trees are:

- **AVL Tree:** It maintains height balance through rotations after insertion and deletion.
- **Treap:** It combines the binary search tree property with randomly assigned priorities to maintain a heap structure.
- **Scapegoat Tree:** It restores balance by rebuilding subtrees when certain conditions are met.

## Requirements and Running Instructions

This project was developed using Python 3.12. The benchmark results are visualized using `matplotlib`.

To install the required packages, I recommend creating a virtual environment first:

```bash
python3 -m venv .venv # Create a virtual environment

source .venv/bin/activate # Activate the environment (macOS/Linux)

python -m pip install -r requirements.txt # Install the required packages
```

All commands should be executed from the project root directory with the virtual environment activated.

To run the unit tests:

```bash
python -m unittest tests.tests -v
```

To run the basic demonstration of the three trees:

```bash
python -m experiments.demo
```

To run benchmark experiments:

```bash
python -m experiments.benchmark # All experiments

python -m experiments.benchmark --experiment scalability # Scalability experiment

python -m experiments.benchmark --experiment insertion-order # Insertion order experiment

python -m experiments.benchmark --experiment deletion # Bulk deletion experiment
```

For the insertion-order experiment, you can select a specific order using `--order ascending`, `--order descending`, or `--order random`. By default, it includes all three insertion orders.

To generate the figures and tables after benchmarking:

```bash
python -m experiments.plot
```

The script automatically generates datasets and reuses them when existing files are the expected size.

### Re-running the Experiments

To save time, the benchmark also checks whether previous measurements are available in `results/benchmarks.csv`. If the required measurements have already been completed, you may see messages such as:

```text
Already measured: random, n=1,000, repeat=1
Already measured: random, n=1,000, repeat=2
Already measured: random, n=1,000, repeat=3
Saved results/benchmarks.csv
```

Please don't panic! :) This means the results are already available, so the benchmark skips those measurements instead of rerunning them. If you would like to run all experiments from scratch, you can back up the existing results before running the benchmark again:

```bash
mv results/benchmarks.csv results/benchmarks_backup.csv
python -m experiments.benchmark
```

Please note that experiments involving 10 million keys may require substantial memory and execution time, depending on your computer's resources, so be aware of this before running them.

## Generated Files

Running the experiments generates the following files:

- `data/*.bin` — generated datasets
- `results/benchmarks.csv` — raw benchmark measurements from individual repetitions
- `results/figures/build_time.png` — comparison of tree construction time
- `results/figures/search_time.png` — comparison of successful search time
- `results/figures/tree_height.png` — comparison of tree height

The following summary tables are also generated in `results/tables/`:

- `scalability.csv` — performance across increasing dataset sizes
- `insertion_order.csv` — comparison of random, ascending, and descending insertions
- `memory_usage.csv` — allocated tree-array memory comparison
- `bulk_deletion.csv` — deletion time and tree height before and after deletion

## Dataset

The experiments use synthetic datasets of distinct, signed 64-bit even integers starting at 0.

To give an example:

```text
0
2
4
6
8
10
```

The experiments are configured as follows:

| Experiment | Dataset | Measurements |
|---|---|---|
| Scalability | 1,000 to 10,000,000 keys | Build time, successful search time, tree height |
| Insertion order | 10,000,000 keys | Build time, tree height |
| Bulk deletion | 10,000,000 keys | Average deletion time, tree height before and after deletion |
| Memory usage | 10,000,000 keys | Allocated tree-array storage |

The bulk deletion experiment randomly selects and removes 60% of the original keys. Successful search performance is evaluated using 50,000 queries. Each experiment is repeated three times, and a fixed random seed is used for reproducibility. The summary tables and plots report the median of the available repetitions.

## Results

The generated figures compare the three tree implementations using the same colors (**red for AVL, blue for Treap, and green for Scapegoat**). If you would rather skip the benchmarks (which is perfectly fine!), you can check the generated figures and CSV tables in the `results/` directory.

### See you in the next project!
