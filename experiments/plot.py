"""Create comparison figures from results/bench_<order>.csv.

Run from project root: python -m experiments.plot --order random
AI-assisted draft: review and disclose its use in the assignment.
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import median

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .dataset import ORDERS

METRICS = {
    "build_s": ("Build time", "Seconds"),
    "search_us": ("Search time", "Microseconds per operation"),
    "insert_us": ("Insertion time", "Microseconds per operation"),
    "delete_us": ("Deletion time", "Microseconds per operation"),
    "mem_mib": ("Array storage", "MiB"),
}


def plot(csv_path, folder):
    """Input: CSV results and output folder. Output: five PNG figures."""
    data = defaultdict(list)
    with csv_path.open(newline="") as f:
        for row in csv.DictReader(f):
            for metric in METRICS:
                data[(metric, row["tree"], int(row["n"]))].append(float(row[metric]))

    if not data:
        raise ValueError(f"No benchmark rows in {csv_path}")
    folder.mkdir(parents=True, exist_ok=True)
    names = sorted({key[1] for key in data})
    for metric, (title, units) in METRICS.items():
        fig, ax = plt.subplots(figsize=(6.5, 4))
        for name in names:
            points = sorted((n, median(values)) for (m, t, n), values in data.items()
                            if m == metric and t == name)
            if points:
                ax.plot([n for n, _ in points], [v for _, v in points],
                        marker="o", label=name.upper() if name == "avl" else name.title())
        ax.set_xscale("log")
        ax.set_xlabel("Number of initial keys (n)")
        ax.set_ylabel(units)
        ax.set_title(title)
        ax.grid(alpha=0.3)
        ax.legend()
        fig.tight_layout()
        dest = folder / f"{metric}_{csv_path.stem.removeprefix('bench_')}.png"
        fig.savefig(dest, dpi=180)
        plt.close(fig)
        print(f"Saved {dest}")


def main():
    """Input: CLI options. Output: figures in results/."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", choices=ORDERS, default="random")
    args = parser.parse_args()
    plot(Path("results") / f"bench_{args.order}.csv", Path("results"))


if __name__ == "__main__":
    main()
