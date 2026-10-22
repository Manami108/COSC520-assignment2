"""Create line plots and a summary CSV for the tree benchmarks.

From the project root:
    python3 -m experiments.plot                    # every available order
    python3 -m experiments.plot --order random

AI-assisted revision: review and disclose its use as required by your course.
"""

import argparse
import csv
from math import log2
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt

from .benchmark import result_path
from .dataset import ORDERS

RESULTS = Path("results")
TREES = ("avl", "treap", "scapegoat")
COLORS = {"avl": "red", "treap": "blue", "scapegoat": "green"}
NAMES = {"avl": "AVL", "treap": "Treap", "scapegoat": "Scapegoat"}

TIME_METRICS = (
    ("build_s", "Build time", "Seconds"),
    ("search_hit_us", "Successful search", "Microseconds / operation"),
    ("search_miss_us", "Unsuccessful search", "Microseconds / operation"),
    ("insert_us", "Insertion", "Microseconds / operation"),
    ("delete_us", "Deletion", "Microseconds / operation"),
    ("shrink_us", "60% bulk deletion", "Microseconds / operation"),
)
STRUCTURE_METRICS = (
    ("height", "Tree height", "Levels (as reported by tree.height())"),
    ("avg_depth", "Average successful search depth", "Nodes visited"),
    ("mem_mib", "Array storage", "MiB (tree.storage_bytes())"),
)
SUMMARY_METRICS = (
    "build_s", "search_hit_us", "search_miss_us", "insert_us", "delete_us",
    "shrink_us", "height", "avg_depth", "mem_mib", "height_60",
)


def read_rows(order):
    with result_path(order).open(newline="") as f:
        return list(csv.DictReader(f))


def median_rows(rows, order):
    """One row per tree and dataset size (median across repetitions)."""
    groups = {}
    for row in rows:
        groups.setdefault((row["tree"], int(row["n"])), []).append(row)

    summaries = []
    for (tree, n), group in sorted(groups.items(), key=lambda item: (item[0][1], item[0][0])):
        summary = {"order": order, "tree": tree, "n": n, "repeats": len(group)}
        for metric in SUMMARY_METRICS:
            readings = [float(r[metric]) for r in group if r.get(metric, "") != ""]
            summary[metric] = median(readings) if readings else ""
        summaries.append(summary)
    return summaries


def save(fig, name):
    folder = RESULTS / "figures"
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / f"{name}.png"
    fig.savefig(dest, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {dest}")


def short_n(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:g}M"
    if n >= 1_000:
        return f"{n / 1_000:g}k"
    return str(n)


def plot_metrics(rows, metrics, order, category, shape):
    """Compare three tree types as dataset size increases."""
    sizes = sorted({r["n"] for r in rows})
    fig, axes = plt.subplots(*shape,
                             figsize=(14, 8 if shape[0] == 2 else 4.5),
                             squeeze=False, constrained_layout=True)

    for ax, (metric, title, unit) in zip(axes.flat, metrics):
        for tree in TREES:
            points = [(r["n"], r[metric]) for r in rows
                      if r["tree"] == tree and r[metric] != ""]
            if points:
                x, y = zip(*points)
                ax.plot(x, y, color=COLORS[tree], marker="o", linewidth=1.8,
                        label=NAMES[tree])

        if metric == "height":
            # A reference growth curve, not another measured tree.
            ax.plot(sizes, [log2(n + 1) for n in sizes],
                    linestyle="--", color="gray", linewidth=1.2,
                    label="log₂(n+1) guide")
        if len(sizes) > 1:
            ax.set_xscale("log")
        if metric in ("build_s", "mem_mib") and all(
                r[metric] > 0 for r in rows if r[metric] != ""):
            ax.set_yscale("log")
        ax.set_xticks(sizes, [short_n(n) for n in sizes], fontsize=8)
        ax.set(title=title, xlabel="Number of keys (n)", ylabel=unit)
        ax.grid(alpha=0.23, which="both")
        if metric == "height":
            ax.legend(fontsize=8)

    # The other panels all use the same three-color key.
    axes.flat[0].legend(fontsize=8)
    fig.suptitle(f"AVL vs Treap vs Scapegoat — {category} ({order} insertion)")
    save(fig, f"{category}_{order}")


def save_summary(rows):
    """CSV table, including all selected insertion orders and sizes."""
    RESULTS.mkdir(parents=True, exist_ok=True)
    dest = RESULTS / "summary.csv"
    fieldnames = ("order", "tree", "n", "repeats", *SUMMARY_METRICS)
    with dest.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {dest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", choices=(*ORDERS, "all"), default="all")
    args = parser.parse_args()

    selected = ORDERS if args.order == "all" else (args.order,)
    available = [order for order in selected if result_path(order).exists()]
    if not available:
        parser.error("No results found. Run python3 -m experiments.benchmark first.")

    all_summaries = []
    for order in available:
        rows = median_rows(read_rows(order), order)
        if not rows:
            print(f"Skipping empty benchmark file for {order}")
            continue
        all_summaries.extend(rows)
        plot_metrics(rows, TIME_METRICS, order, "times", (2, 3))
        plot_metrics(rows, STRUCTURE_METRICS, order, "structure", (1, 3))

    if all_summaries:
        save_summary(all_summaries)
    missing = set(selected) - set(available)
    if missing:
        print("Missing orders (run the benchmark first): " + ", ".join(sorted(missing)))


if __name__ == "__main__":
    main()
