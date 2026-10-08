"""Create PNG/PDF figures; matplotlib is used only for visualization."""

import argparse
import csv
from pathlib import Path


def plot_results(results):
    """Input: results directory. Output: figures for each order/workload pair."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    results = Path(results)
    with (results / "summary.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError("Summary contains no results")
    output = results / "plots"
    output.mkdir(exist_ok=True)
    colors = {"avl": "#3569b1", "treap": "#d97725", "splay": "#398264"}
    labels = {"avl": "AVL", "treap": "Treap", "splay": "Splay"}
    pairs = sorted({(row["order"], row["workload"]) for row in rows})

    def draw(axis, subset, field, ylabel, operation=None, log_y=False):
        """Input: axis/data/metric. Output: drawn lines and observed min-max band."""
        for name in ("avl", "treap", "splay"):
            data = sorted([row for row in subset if row["algorithm"] == name
                           and (operation is None or row["operation"] == operation)],
                          key=lambda row: int(row["n"]))
            if not data:
                continue
            x = [int(row["n"]) for row in data]
            y = [float(row[field]) for row in data]
            axis.plot(x, y, "o-", color=colors[name], label=labels[name], markersize=4)
            if field == "median_us":
                axis.fill_between(x, [float(row["min_us"]) for row in data],
                                  [float(row["max_us"]) for row in data],
                                  color=colors[name], alpha=0.14)
        axis.set_xscale("log")
        if log_y:
            axis.set_yscale("log")
        axis.set_xlabel("Initial distinct keys n (log scale)")
        axis.set_ylabel(ylabel)
        axis.grid(alpha=0.22)
        axis.legend(frameon=False)

    def save(fig, stem):
        """Input: figure/file stem. Output: PNG and vector PDF files."""
        fig.savefig(output / f"{stem}.png", dpi=180, bbox_inches="tight")
        fig.savefig(output / f"{stem}.pdf", bbox_inches="tight")
        plt.close(fig)

    for order, workload in pairs:
        subset = [row for row in rows if row["order"] == order and row["workload"] == workload]
        fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
        for axis, operation in zip(axes.flat, ("build", "search", "insert", "delete")):
            draw(axis, subset, "median_us", "Median microseconds / operation", operation)
            axis.set_title({"build": "Build: average insertion cost",
                            "search": "Membership lookup", "insert": "Insert new keys",
                            "delete": "Delete original keys"}[operation])
        fig.suptitle(f"Ordered-set performance | {order} insertion | {workload} search\n"
                     "Shading: observed min-max across repetitions (not confidence intervals)", fontsize=12)
        save(fig, f"operations_{order}_{workload}")
        fig, axis = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
        draw(axis, subset, "median_seconds", "Total build seconds (log scale)", "build", True)
        axis.set_title(f"Total construction time | {order} | {workload}")
        save(fig, f"build_{order}_{workload}")
        memory = [dict(row, memory_mib=float(row["median_tree_array_bytes"]) / (1 << 20))
                  for row in subset if row["operation"] == "build"]
        fig, axis = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
        draw(axis, memory, "memory_mib", "Tree arrays after build (MiB)")
        axis.set_title(f"Allocated array storage | {order} | {workload}\n"
                       "Includes capacity and headers; excludes process/data/workload memory", fontsize=11)
        save(fig, f"memory_{order}_{workload}")
    print(f"Saved figures in {output}")


def main():
    """Input: CLI results directory. Output: saved comparison figures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path("results/quick"))
    args = parser.parse_args()
    plot_results(args.results)


if __name__ == "__main__":
    main()
