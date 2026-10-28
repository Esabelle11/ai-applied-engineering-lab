# Parallel Tool-Augmented Solver

This pattern composes independent solver attempts, a bounded model/tool
feedback loop, pooled execution resources, and deterministic consensus.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/08_reasoning_and_execution/parallel_tool_augmented_solver/run.py
```

The example uses a deterministic calculator executor and never executes model
generated Python. `LocalKernelSandbox` is available for trusted local
experiments; it is not a security boundary. Use `DockerPythonSandbox` when the
execution boundary must be isolated.
