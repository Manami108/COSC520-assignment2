"""Create three scaling plots and two comparison tables from benchmark results.

From the project root:
    python3 -m experiments.plot

AI-assisted revision: review and disclose its use as required by the course.
"""

import csv
from math import log2
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt

from .benchmark import RESULT_FILE, REPEATS
from .dataset import DELETION_SIZE, ORDERS, ORDER_SIZE, SCALING_SIZES

RESULTS = Path("results")
TREES = ("avl", "treap", "scapegoat")
NAMES = {"avl": "AVL", "treap": "Treap", "scapegoat": "Scapegoat"}
COLORS = {"avl": "red", "treap": "blue", "scapegoat": "green"}


def read_rows():
    """Read raw measurements and cast numeric fields for aggregation."""
    with RESULT_FILE.open(newline="") as f:
        return list(csv.DictReader(f))


def summaries(rows):
    """Return median metrics for each tree, insertion order, and size."""
    groups = {}
    for row in rows:
        key = (row["tree"], row["order"], int(row["n"]))
        groups.setdefault(key, []).append(row)

    results = {}
    for key, group in groups.items():
        result = {"repeats": len(group)}
        for field in ("build_s", "search_hit_us", "height", "deleted",
                      "bulk_delete_us", "height_after_delete"):
            values = [float(r[field]) for r in group if r.get(field, "") != ""]
            result[field] = median(values) if values else ""
        results[key] = result
    return results


def write_table(name, columns, rows):
    """Write a concise report-ready CSV table."""
    folder = RESULTS / "tables"
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / name
    with dest.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {dest}")


def size_label(n):
    """Format an x-axis dataset size using K/M units."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:g}M"
    if n >= 1_000:
        return f"{n / 1_000:g}K"
    return str(n)


def plot_scaling(stats):
    """One line plot each for build time, successful search, and tree height."""
    plots = (
        ("build_s", "build_time.png", "Build time", "Seconds"),
        ("search_hit_us", "search_time.png", "Successful search", "Microseconds per search"),
        ("height", "tree_height.png", "Tree height", "Levels reported by tree.height()"),
    )
    folder = RESULTS / "figures"
    folder.mkdir(parents=True, exist_ok=True)

    for field, filename, title, unit in plots:
        fig, ax = plt.subplots(figsize=(6.3, 4.1), constrained_layout=True)
        found = False
        for tree in TREES:
            points = [(n, stats[(tree, "random", n)][field])
                      for n in SCALING_SIZES
                      if (tree, "random", n) in stats
                      and stats[(tree, "random", n)][field] != ""]
            if not points:
                continue
            found = True
            ax.plot([n for n, value in points], [value for n, value in points],
                     linewidth=1.8, color=COLORS[tree], label=NAMES[tree])

        if not found:
            plt.close(fig)
            continue
        if field == "height":
            sizes = [n for n in SCALING_SIZES
                     if any((tree, "random", n) in stats for tree in TREES)]
            ax.plot(sizes, [log2(n + 1) for n in sizes], "--", color="gray",
                    linewidth=1.3, label="log₂(n+1) reference")
        ax.set_xscale("log")
        if field == "build_s":
            ax.set_yscale("log")
        ax.set_xticks(SCALING_SIZES, [size_label(n) for n in SCALING_SIZES])
        ax.set(title=title, xlabel="Number of keys (n)", ylabel=unit)
        ax.grid(alpha=0.25, which="both")
        ax.legend(fontsize=9)
        dest = folder / filename
        fig.savefig(dest, dpi=220, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved {dest}")


def save_tables(stats):
    """Save the scaling measurements and the two fixed-size comparisons."""
    scaling = []
    for n in SCALING_SIZES:
        for tree in TREES:
            values = stats.get((tree, "random", n))
            if values:
                scaling.append({"n": n, "tree": NAMES[tree],
                                "build_s": values["build_s"],
                                "search_hit_us": values["search_hit_us"],
                                "height": values["height"],
                                "repeats": values["repeats"]})
    if scaling:
        write_table("scalability.csv",
                    ("n", "tree", "build_s", "search_hit_us", "height", "repeats"),
                    scaling)

    by_order = []
    for order in ORDERS:
        for tree in TREES:
            values = stats.get((tree, order, ORDER_SIZE))
            if values:
                by_order.append({"n": ORDER_SIZE, "order": order,
                                 "tree": NAMES[tree], "build_s": values["build_s"],
                                 "height": values["height"],
                                 "repeats": values["repeats"]})
    if by_order:
        write_table("insertion_order.csv",
                    ("n", "order", "tree", "build_s", "height", "repeats"),
                    by_order)

    deletion = []
    for tree in TREES:
        values = stats.get((tree, "random", DELETION_SIZE))
        if values and values["bulk_delete_us"] != "":
            deletion.append({"n": DELETION_SIZE, "tree": NAMES[tree],
                             "deleted": values["deleted"],
                             "deletion_us": values["bulk_delete_us"],
                             "height_before": values["height"],
                             "height_after": values["height_after_delete"],
                             "repeats": values["repeats"]})
    if deletion:
        write_table("bulk_deletion.csv",
                    ("n", "tree", "deleted", "deletion_us", "height_before",
                     "height_after", "repeats"), deletion)


def main():
    if not RESULT_FILE.exists():
        raise SystemExit("No benchmark results yet. Run: python3 -m experiments.benchmark")
    stats = summaries(read_rows())
    plot_scaling(stats)
    save_tables(stats)
    print("Each value is a median across the repetitions present in benchmarks.csv.")


if __name__ == "__main__":
    main()
