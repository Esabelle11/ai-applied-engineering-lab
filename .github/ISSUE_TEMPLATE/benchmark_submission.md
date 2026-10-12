---
name: Benchmark submission
about: Propose reproducible evidence comparing engineering approaches
labels: [benchmark]
---

## Question / hypothesis
What difference are we measuring? State expected effects and possible negative outcomes.

## Controls
Alternatives, identical inputs and fault sequences, seeds, sample sizes, model versions, prompts, hardware and concurrency.

## Dataset and run manifest
Attach non-sensitive/synthetic fixtures, configuration hashes, runtime versions and exact reproduction commands.

## Metrics
Task correctness, tool success, p50/p95 measured latency, usage, cost (null if unknown), error counts, confidence/variance as appropriate.

## Results and limitations
Raw data, summary and failures, uncontrolled provider behavior, known uncertainty. Distinguish scripted fixtures from actual model measurements.
