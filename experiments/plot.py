"""Plot two combined figures from the existing tree benchmark CSV files.

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


def mid(rows, tree, n, metric):
    values = [float(r[metric]) for r in rows
              if r["tree"] == tree and int(r["n"]) == n and r.get(metric)]
    return median(values) if values else None


def save(fig, name):
    folder = RESULTS / "figures"
    folder.mkdir(parents=True, exist_ok=True)
    fig.savefig(folder / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {folder / (name + '.png')}")


def plot(order):
    """Six metrics merged into one comparison figure."""
    rows = load(order)
    sizes = sorted({int(r["n"]) for r in rows})
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
    for ax, (metric, title, ylabel) in zip(axes.flat, METRICS):
        for tree in TREES:
            points = [(n, mid(rows, tree, n, metric)) for n in sizes]
            points = [(n, y) for n, y in points if y is not None]
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
    """Compare insertion orders at their largest common dataset size."""
    if not all((RESULTS / f"bench_{o}.csv").exists() for o in ORDERS):
        return
    data = {o: load(o) for o in ORDERS}
    common = set.intersection(*({int(r["n"]) for r in rows} for rows in data.values()))
    if not common:
        return
    n = max(common)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for ax, metric, title, ylabel in zip(axes, ("build_s", "height"),
                                         ("Build time", "Tree height"),
                                         ("Seconds", "Levels")):
        for tree in TREES:
            values = [mid(data[o], tree, n, metric) for o in ORDERS]
            if all(v is not None for v in values):
                ax.plot(ORDERS, values, label=("AVL" if tree == "avl" else tree.title()))
        ax.set(title=title, ylabel=ylabel)
        ax.grid(alpha=0.2)
    axes[0].legend(fontsize=8)
    fig.suptitle(f"Insertion-order comparison (n={n:,})")
    save(fig, "insertion_order")


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
