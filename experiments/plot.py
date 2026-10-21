"""Plot two combined figures from benchmark CSVs.

Run from project root: python -m experiments.plot --order all
AI-assisted draft: review and disclose its use in the assignment.
"""

import argparse
import csv
from pathlib import Path
from statistics import median

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .dataset import ORDERS

RESULTS = Path("results")
TREES = ("avl", "treap", "scapegoat")
METRICS = (
    ("build_s", "Build time", "Seconds"),
    ("search_us", "Search", "Microseconds / operation"),
    ("insert_us", "Extra insertion", "Microseconds / operation"),
    ("delete_us", "Deletion", "Microseconds / operation"),
    ("height", "Tree height", "Levels"),
    ("avg_depth", "Average search depth", "Nodes visited"),
)


def load(order):
    with (RESULTS / f"bench_{order}.csv").open(newline="") as file:
        return list(csv.DictReader(file))


def vals(rows, tree, n, metric):
    """Return all repetitions for one tree, size, and metric."""
    return [float(r[metric]) for r in rows
            if r["tree"] == tree and int(r["n"]) == n and r.get(metric)]


def save(fig, name):
    folder = RESULTS / "figures"
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / f"{name}.png"
    fig.savefig(dest, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {dest}")


def plot(order):
    """Plot six performance and structure metrics in one figure."""
    rows = load(order)
    sizes = sorted({int(r["n"]) for r in rows})
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
    for ax, (metric, title, ylabel) in zip(axes.flat, METRICS):
        for tree in TREES:
            points = [(n, median(v)) for n in sizes
                      if (v := vals(rows, tree, n, metric))]
            if points:
                x, y = zip(*points)
                ax.plot(x, y, label=("AVL" if tree == "avl" else tree.title()))
        if len(sizes) > 1:
            ax.set_xscale("log")
        ax.set(title=title, xlabel="Number of keys", ylabel=ylabel)
        ax.grid(alpha=0.2)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle(f"AVL vs Treap vs Scapegoat — {order} insertion")
    save(fig, f"summary_{order}")


def orders():
    """Grouped bars with min–max ranges across benchmark repetitions."""
    missing = [o for o in ORDERS if not (RESULTS / f"bench_{o}.csv").exists()]
    if missing:
        print(f"Skipping order comparison; missing CSVs for: {', '.join(missing)}")
        return
    data = {order: load(order) for order in ORDERS}
    common = set.intersection(*({int(r["n"]) for r in rows} for rows in data.values()))
    if not common:
        print("Skipping order comparison; no dataset size appears in every CSV")
        return
    n = max(common)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    width = 0.25

    for ax, metric, title, ylabel in zip(
            axes, ("build_s", "height"), ("Build time", "Tree height"),
            ("Seconds", "Levels")):
        for i, tree in enumerate(TREES):
            xs, mids, low, high = [], [], [], []
            for j, order in enumerate(ORDERS):
                samples = vals(data[order], tree, n, metric)
                if not samples:
                    continue
                m = median(samples)
                xs.append(j + (i - 1) * width)
                mids.append(m)
                low.append(m - min(samples))
                high.append(max(samples) - m)
            if xs:
                ax.bar(xs, mids, width=width,
                       yerr=[low, high], capsize=3,
                       label=("AVL" if tree == "avl" else tree.title()))
        ax.set_xticks(range(len(ORDERS)), ORDERS)
        ax.set(title=title, ylabel=ylabel)
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)
    axes[0].legend(fontsize=8)
    fig.suptitle(f"Insertion-order comparison (n={n:,}; bars = medians, whiskers = min–max)")
    save(fig, "insertion_order")

    print(f"\nBuild-time variation at n={n:,} (seconds):")
    print(f"{'Order':<12} {'Tree':<12} {'Reps':>4} {'Min':>8} {'Median':>8} {'Max':>8}")
    for order in ORDERS:
        for tree in TREES:
            samples = vals(data[order], tree, n, "build_s")
            if samples:
                print(f"{order:<12} {tree:<12} {len(samples):>4} "
                      f"{min(samples):>8.3f} {median(samples):>8.3f} {max(samples):>8.3f}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", choices=(*ORDERS, "all"), default="random")
    args = parser.parse_args()
    order = "random" if args.order == "all" else args.order
    if not (RESULTS / f"bench_{order}.csv").exists():
        parser.error(f"Missing results/bench_{order}.csv")
    plot(order)
    if args.order == "all":
        orders()


if __name__ == "__main__":
    main()
