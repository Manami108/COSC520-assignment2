# Benchmark output

`sample/` contains real execution results from the quick profile during project
creation. They cover only 1,000 to 20,000 keys. Interpret them as a pipeline
demonstration, not final evidence about ten million keys or another computer.

`scale-check/` adds one repetition per tree at 100,000 and 1,000,000 keys,
random insertion and uniform search. Its main purpose is to verify the large
job path; one repetition is not enough to assess timing variability.

Generate your own measurements into a new directory using the README commands.
Keep raw observations and metadata together with summary tables and figures.
The full profile reaches ten million keys; it was not run during initial creation.
