"""Test dataset reproducibility, workload answers, and benchmark integration."""

import csv
import json
from pathlib import Path
import tempfile
import unittest

from experiments.benchmark import read_config, run
from experiments.dataset import generate_dataset, load_dataset
from experiments.summarize import summarize
from experiments.worker import run_job, timed_batch
from experiments.workloads import search_queries, update_queries
from structures import TREE_TYPES


class ExperimentTests(unittest.TestCase):
    """Verify experimental inputs and output metrics against known answers."""

    def test_datasets_roundtrip_and_reproducible_bytes(self):
        """All orders have the same universe; seeded compressed bytes repeat."""
        with tempfile.TemporaryDirectory() as directory:
            for order in ("random", "ascending", "descending"):
                paths = [Path(directory) / f"{order}_{i}.gz" for i in range(2)]
                manifests = [generate_dataset(path, 200, order, 37) for path in paths]
                self.assertEqual(manifests[0]["sha256"], manifests[1]["sha256"])
                values = list(load_dataset(paths[0]))
                self.assertEqual(sorted(values), list(range(200)))
                if order == "ascending":
                    self.assertEqual(values, list(range(200)))
                if order == "descending":
                    self.assertEqual(values, list(range(199, -1, -1)))

    def test_dataset_hash_and_length_corruption_are_detected(self):
        """Reject changed compressed bytes and incorrect manifest lengths."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.gz"
            generate_dataset(path, 20)
            manifest_path = path.with_suffix(path.suffix + ".json")
            metadata = json.loads(manifest_path.read_text())
            metadata["n"] = 21
            manifest_path.write_text(json.dumps(metadata))
            with self.assertRaises(ValueError):
                load_dataset(path)
            generate_dataset(path, 20)
            path.write_bytes(path.read_bytes() + b"corrupt")
            with self.assertRaisesRegex(ValueError, "checksum"):
                load_dataset(path)

    def test_workloads_have_correct_hits_and_distinct_updates(self):
        """Derive ground truth from integer ranges rather than tree behavior."""
        for n in (1, 7, 1000):
            for workload in ("uniform", "hotspot", "sequential"):
                queries, expected = search_queries(n, 101, workload, 91)
                self.assertEqual(sum(0 <= key < n for key in queries), expected)
                self.assertEqual(queries, search_queries(n, 101, workload, 91)[0])
            additions, deletions = update_queries(n, 2000)
            self.assertEqual(len(set(additions)), min(n, 2000))
            self.assertEqual(len(set(deletions)), min(n, 2000))
            self.assertTrue(all(key >= n for key in additions))
            self.assertTrue(all(0 <= key < n for key in deletions))
            self.assertFalse(set(additions) & set(deletions))

    def test_worker_all_algorithms_and_workloads(self):
        """A complete job must verify all four operation counts and timings."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.gz"
            manifest = generate_dataset(path, 100)
            for algorithm in TREE_TYPES:
                for workload in ("uniform", "hotspot", "sequential"):
                    rows = run_job({"algorithm": algorithm, "dataset": str(path),
                                    "dataset_sha256": manifest["sha256"], "n": 100,
                                    "order": "random", "workload": workload, "repeat": 0,
                                    "seed": 42, "treap_seed": 42, "queries": 101,
                                    "updates": 20, "warmup": 10, "validate_limit": 100})
                    self.assertEqual([row["operation"] for row in rows], ["build", "search", "insert", "delete"])
                    self.assertEqual([row["successes"] for row in rows],
                                     [100, 50 if workload == "uniform" else 101, 20, 20])
                    self.assertTrue(all(row["seconds"] >= 0 for row in rows))
                    self.assertTrue(all(row["tree_array_bytes"] > 0 for row in rows))

    def test_timer_restores_gc_after_exception(self):
        """A measured operation raising an error must not leave GC disabled."""
        import gc
        old = gc.isenabled()
        gc.enable()
        try:
            def failure(value):
                raise RuntimeError("intentional")
            with self.assertRaises(RuntimeError):
                timed_batch(failure, [1])
            self.assertTrue(gc.isenabled())
        finally:
            if not old:
                gc.disable()

    def test_config_validation(self):
        """Reject misspelled fields, invalid dimensions, and duplicate sizes."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            for config in ({"sizes": []}, {"sizes": [1], "repeats": 0},
                           {"sizes": [1, 1]}, {"sizes": [1], "algorithm": "avl"},
                           {"sizes": [1], "workloads": ["unknown"]}):
                path.write_text(json.dumps(config))
                with self.assertRaises(ValueError):
                    read_config(path)

    def test_subprocess_runner_summary_and_resume(self):
        """Run real subprocesses, verify medians, resume, and config guards."""
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            config_path = directory / "config.json"
            config_path.write_text(json.dumps({"sizes": [50], "repeats": 2,
                                              "queries": 31, "updates": 10, "warmup": 5}))
            config = read_config(config_path)
            output = directory / "results"
            run(config, output, directory / "data")
            with (output / "raw.csv").open(newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 24)
            summary = summarize(output / "raw.csv", output)
            self.assertEqual(len(summary), 12)
            for row in summary:
                raw = [float(item["us_per_operation"]) for item in rows
                       if item["algorithm"] == row["algorithm"] and item["operation"] == row["operation"]]
                self.assertAlmostEqual(row["median_us"], sum(raw) / 2)
            before = (output / "raw.csv").read_bytes()
            run(config, output, directory / "data", resume=True)
            self.assertEqual(before, (output / "raw.csv").read_bytes())
            with self.assertRaises(FileExistsError):
                run(config, output, directory / "data")
            with self.assertRaises(ValueError):
                run(config | {"seed": 99}, output, directory / "data", resume=True)


if __name__ == "__main__":
    unittest.main()
