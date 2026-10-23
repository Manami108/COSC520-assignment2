# Plot scaling results and create summary tables
import csv
from math import ceil, log2
from pathlib import Path
from statistics import median
import matplotlib.pyplot as plt
from .benchmark import RESULT_FILE
from .dataset import DELETION_SIZE, ORDERS, ORDER_SIZE, SCALING_SIZES

RESULTS = Path("results")
TREES = ("avl", "treap", "scapegoat")
NAMES = {"avl": "AVL", "treap": "Treap", "scapegoat": "Scapegoat"}
COLORS = {"avl": "red", "treap": "blue", "scapegoat": "green"}

def read_rows():
    with RESULT_FILE.open(newline="") as f:
        return list(csv.DictReader(f))

def summaries(rows):
    # The code groups results by tree, insertion order, and size, then calculates medians.
    groups = {}
    for row in rows:
        key = (row["tree"], row["order"], int(row["n"]))
        groups.setdefault(key, []).append(row)

    results = {}
    for key, group in groups.items():
        result = {"repeats": len(group)}
        for field in ("build_s", "search_hit_us", "height", "memory_mib",
                      "deleted", "bulk_delete_us", "height_after_delete"):
            values = [float(row[field]) for row in group if row.get(field, "") != ""]
            result[field] = median(values) if values else ""
        results[key] = result
    return results

def write_table(filename, columns, rows):
    # This block saves summarized results as CSV tables
    folder = RESULTS / "tables"
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / filename
    with dest.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {dest}")

def size_label(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:g}M"
    if n >= 1_000:
        return f"{n / 1_000:g}K"
    return str(n)

def plot_scaling(stats): # this block plots build time, search time, and height against dataset size.
    plots = (
        ("build_s", "build_time.png", "Build time", "Seconds"),
        ("search_hit_us", "search_time.png", "Successful search", "Microseconds per search"),
        ("height", "tree_height.png", "Tree height", "Height (nodes)"),
    )
    folder = RESULTS / "figures"
    folder.mkdir(parents=True, exist_ok=True)

    for field, filename, title, unit in plots:
        fig, ax = plt.subplots(figsize=(6.3, 4.1), constrained_layout=True)
        sizes = []
        for tree in TREES:
            points = [(n, stats[(tree, "random", n)][field])
                      for n in SCALING_SIZES
                      if (tree, "random", n) in stats
                      and stats[(tree, "random", n)][field] != ""]
            if not points:
                continue
            sizes.extend(n for n, _ in points)
            ax.plot([n for n, _ in points], [value for _, value in points],
                    linewidth=1.8, color=COLORS[tree], label=NAMES[tree])
        if not sizes:
            plt.close(fig)
            continue
        sizes = sorted(set(sizes))

        # Reference curves (minimum height = ceil(log2(n+1)))
        # build time ~ n*log2(n), and search time ~ log2(n)
        if field == "height":
            ax.plot(sizes, [ceil(log2(n + 1)) for n in sizes], "--",
                color="gray", label="⌈log₂(n+1)⌉ (minimum height)")
        else:
            shape = (lambda n: n * log2(n)) if field == "build_s" else log2
            anchor_n = sizes[0]
            anchor = next((stats[(tree, "random", anchor_n)][field]
                           for tree in TREES
                           if (tree, "random", anchor_n) in stats
                           and stats[(tree, "random", anchor_n)][field] != ""), None)
            if anchor is not None and anchor > 0:
                scale = anchor / shape(anchor_n)
                label = "n log₂(n) (scaled)" if field == "build_s" else "log₂(n) (scaled)"
                ax.plot(sizes, [scale * shape(n) for n in sizes], "--",
                        color="gray", label=label)

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
    # This code generates CSV tables for scalability, insertion order, memory, and deletion.
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
    memory = []
    for tree in TREES:
        values = stats.get((tree, "random", ORDER_SIZE))
        if values and values["memory_mib"] != "":
            memory.append({"n": ORDER_SIZE, "tree": NAMES[tree],
                           "memory_mib": values["memory_mib"],
                           "repeats": values["repeats"]})

        values = stats.get((tree, "random", DELETION_SIZE))
        if values and values["bulk_delete_us"] != "":
            deletion.append({"n": DELETION_SIZE, "tree": NAMES[tree],
                             "deleted": values["deleted"],
                             "deletion_us": values["bulk_delete_us"],
                             "height_before": values["height"],
                             "height_after": values["height_after_delete"],
                             "repeats": values["repeats"]})
    if memory:
        write_table("memory_usage.csv", ("n", "tree", "memory_mib", "repeats"), memory)
    if deletion:
        write_table("bulk_deletion.csv",
                    ("n", "tree", "deleted", "deletion_us", "height_before",
                     "height_after", "repeats"), deletion)

def main():
    stats = summaries(read_rows())
    plot_scaling(stats)
    save_tables(stats)
    print("Values are medians across available repetitions.")

if __name__ == "__main__":
    main()
