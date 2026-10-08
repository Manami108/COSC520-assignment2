"""Produce medians/ranges and a Markdown performance table from raw CSV."""

import argparse
import csv
from pathlib import Path
import statistics

GROUP = ["algorithm", "n", "order", "workload", "operation"]


def summarize(raw_path, output):
    """Input: raw CSV/output directory. Output: summary rows and saved tables."""
    groups = {}
    with Path(raw_path).open(newline="") as stream:
        for row in csv.DictReader(stream):
            key = tuple(row[field] for field in GROUP)
            groups.setdefault(key, []).append(row)
    rows = []
    for key in sorted(groups, key=lambda key: (key[2], key[3], key[4], int(key[1]), key[0])):
        observations = groups[key]
        times = [float(row["us_per_operation"]) for row in observations]
        rows.append(dict(zip(GROUP, key)) | {
            "samples": len(times), "operations": observations[0]["operations"],
            "median_seconds": statistics.median(float(row["seconds"]) for row in observations),
            "median_us": statistics.median(times), "min_us": min(times), "max_us": max(times),
            "median_tree_array_bytes": statistics.median(int(row["tree_array_bytes"]) for row in observations),
        })
    if not rows:
        raise ValueError("Raw CSV contains no benchmark observations")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with (output / "summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# Measured performance", "", "Generated from raw.csv; time is batch median.", "",
             "| Order | Workload | n | Structure | Operation | Median seconds | Median us/op | Min-max us/op | Repeats |",
             "| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: |"]
    for row in rows:
        lines.append(f"| {row['order']} | {row['workload']} | {int(row['n']):,} | {row['algorithm']} | "
                     f"{row['operation']} | {row['median_seconds']:.6f} | {row['median_us']:.4f} | "
                     f"{row['min_us']:.4f}-{row['max_us']:.4f} | {row['samples']} |")
    (output / "performance_table.md").write_text("\n".join(lines) + "\n")
    return rows


def main():
    """Input: CLI results directory. Output: regenerated CSV and Markdown table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path("results/quick"))
    args = parser.parse_args()
    summarize(args.results / "raw.csv", args.results)


if __name__ == "__main__":
    main()
