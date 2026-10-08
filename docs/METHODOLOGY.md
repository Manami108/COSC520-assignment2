# Experimental methodology

## Comparable input and operation semantics

At size n, every dataset contains exactly the keys [0,n), once each. Random,
ascending, and descending orders change only insertion order. All algorithms
receive the same saved input for a given size/order/seed. The dataset and query
sequences are prepared before timing. The same dataset is reused across
repetitions; treap priority seeds vary by repetition (seed + 1009*repeat).

The program measures four phases:

| Phase | Initial state | Measured sequence | Ground-truth checks |
| --- | --- | --- | --- |
| Build | Empty tree | Insert all n distinct dataset keys | n successes and size n |
| Search | Built tree, after untimed warmup | q membership calls for one workload | Exact expected hit count |
| Insert | State left by that search workload | u distinct new keys in [n,n+u) | u successes and size n+u |
| Delete | State left by insertion | u distinct original keys sampled from [0,n) | u successes and final size n |

Here u=min(n, configured update count). A delete is always a successful deletion
of an original key, not a deletion of the just-added keys. Insert/delete phases
are part of this documented sequence and do not claim independent initial
states. In particular, splay update costs can depend on the earlier search.

## Search workloads

| Workload | Hits | Sequence |
| --- | --- | --- |
| Uniform | Exactly floor(q/2) | Uniform present draws plus distinct misses [n,n+ceil(q/2)), shuffled |
| Hotspot | q | 80% probability of a draw from first min(128,n) keys, otherwise uniform present draw |
| Sequential | q | 0,1,...,n-1 cycling as needed |

The hot region also appears in the 20% uniform branch, so its actual probability
is slightly above 80%. Repeated query keys are intentional. Uniform misses lie
above the stored range; they do not represent arbitrary gaps or misses below
the minimum. This is a workload limitation to discuss in the report, not a
universal model of all failed searches. You can design an additional gap-based
workload as a genuine student contribution.

Each workload has a fresh tree in a separate worker job. Search starts after
the configured prefix warmup; the timed batch then executes the complete
precomputed query sequence, including that prefix again. Splay access adapts
the tree during both warmup and measurement. The large-build member probes
use non-splaying base search so they do not alter the initial tree shape.

## Timing

`time.perf_counter_ns` times only each operation loop. Loop overhead, key
validation, method dispatch, rotations, allocation, and priority generation
inside insertion are included. Dataset generation, decompression, hashing,
query construction, process startup, invariant checks, and plotting are excluded.
Cyclic garbage collection is disabled only during a timed batch. Allocation
and reference counting still occur normally.

Raw rows retain every repetition. Summaries use the median, with min/max for
context. Plot shading is the observed range, not a statistical confidence
interval. Three repetitions are a practical default, not strong statistical
evidence. Vary seeds separately if studying robustness to different datasets.
Per-operation numbers are whole-batch averages, not individual latency percentiles.

Each job runs in a new Python process. Algorithm order is seeded and shuffled
within each repetition to reduce systematic run-order bias. The harness does
not pin CPU cores, control frequency, or flush CPU caches. Run on an otherwise
quiet machine and report its specifications. Fresh-process isolation does not
remove filesystem cache effects or concurrent system activity.

## Correctness checks

Small jobs run full structural validation before search and after updates.
Large jobs avoid O(n) debug sets: they check build count/cardinality and 100
known members, search hits, update counts, and all added/deleted keys afterward.
This is not exhaustive structural validation at ten million nodes; randomized
unit tests and smaller complete validations complement these probes.

## Memory

`tree_array_bytes` is the allocated size of tree arrays, including headers,
spare capacity, and recycled slots at the end of the named phase. It excludes
the dataset, workloads, instance object, random generator, and temporary stacks.
`job_peak_rss_bytes` is the OS-reported high-water resident memory for the entire
worker, including data, interpreter, verification, and all phases. On Windows
it is unavailable and recorded as blank. It is not per-phase tree memory.

Do not compare the array-byte figure directly with total process RSS. Array
storage follows historical peak allocated nodes, because deletion recycles
slots without shrinking arrays.

## Interpretation cautions

Use total build time when discussing construction complexity. Dividing build
time by n gives average insertion cost, not total cost. Use q-normalized search
cost when query counts are fixed. Expected treap bounds and amortized splay
bounds do not promise logarithmic worst-case latency for each call.
Python constant factors, memory locality, finite scales, skewed queries, and
splay state changes can explain runtime differences. Do not infer an
asymptotic class from one small timing plot. Source/environment hashes and the
exact data manifests are saved so results can be traced to the tested code.
