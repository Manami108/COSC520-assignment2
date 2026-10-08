# Validation performed during creation

Checked on 2026-10-08, Python 3.12.14 on Linux. Detailed environment and
source fingerprints appear in each results directory's `metadata.json`.

| Check | Actual result |
| --- | --- |
| Standard-library unit/integration suite | 17 tests passed |
| Randomized differential tree testing | 36,000 mixed operations across three structures and twenty seeds |
| Degenerate splay tree | 20,000 sorted insertions, full invariant checks, deep access, and deletion passed |
| Demonstration | All three structures produced correct insert/search/delete behavior |
| Quick profile | 108 isolated jobs completed, four operations each, three repeats; maximum n=20,000 |
| Scale-check profile | Six isolated jobs completed; each structure checked at n=100,000 and n=1,000,000, one repetition |
| Ten-million-key dataset | Gzip decompression, SHA-256 verification, exact count, range, and duplicate-free coverage checked |
| Dataset coverage check | A 1.25 MB bitset independently verified every key in [0,10,000,000) occurs exactly once |
| Figures | Timing, construction, and storage figures generated as PNG and vector PDF; representative layouts visually inspected |
| Python packaging | Wheel built without downloading dependencies; JSON profiles included |
| GitHub CI | Workflow supplied; not run on GitHub or on Windows/macOS during creation |
| Full profile through ten million nodes | Not run; configuration and actual input dataset included |
| Repository and dataset publication | Not performed |
| Student-authored contribution | None claimed in the initial package |

The quick/scale checks verify that the workflow runs; they are not a controlled
final performance study. Dataset generation and figure preparation overlapped
some creation-time measurements, so rerun the experiments on an otherwise
quiet computer before making final performance claims. A single scale-check
repetition supplies no estimate of timing variability.

The source fingerprints of supplied measurements match the supplied algorithm
and experiment source. Do not combine new-source results with these observations
as though they were all measured from the same implementation. Use a new output
directory after modifying the code.

At one million keys, all workers completed their known-answer checks. Complete
structural validation is limited to configured smaller jobs; the large path
uses documented probes and batch answer/cardinality checks. Support for ten
million keys is implemented but actual ten-million-node execution remains to be
verified by running the full profile.
