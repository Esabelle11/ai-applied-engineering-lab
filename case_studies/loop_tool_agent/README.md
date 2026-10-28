# Loop Tool Agent

This case study is a small, readable version of a tool-using math agent.

```text
LLM → Python tool request → Jupyter execution → tool feedback → LLM → consensus
```

## Read the project in this order

| File | What it teaches |
| --- | --- |
| [`data.py`](data.py) | Load and reproducibly sample questions from the CSV. |
| [`agent.py`](agent.py) | The bounded model/tool feedback loop and its JSON protocol. |
| [`run.py`](run.py) | CLI safety checks, sandbox setup, attempts, and consensus. |
| [`data/50problems.csv`](data/50problems.csv) | The 50-question math dataset with expected answers. |

The model can make only two kinds of JSON response:

```json
{"action":"python","code":"print(6 * 7)"}
```

```json
{"action":"answer","answer":42}
```

`agent.py` executes the first response, sends its stdout back to the model,
then accepts the second response only after at least one Python verification.

## Run one live question

The Jupyter runtime is optional because it runs model-generated Python with
your local user permissions. It is for trusted local experiments only—not a
security sandbox for arbitrary users or models.

```bash
# Install the trusted-local Jupyter runtime once.
uv sync --extra local-kernel

# Configure AI_LAB_PROVIDER, AI_LAB_MODEL, and its API key in .env.
# One question, at most three model requests.
uv run --extra local-kernel python -m case_studies.loop_tool_agent.run \
  --live --trusted-local-kernel
```

For genuine consensus, use two independent two-turn attempts. The hard limit
is four possible model requests, so it cannot accidentally run all 50 rows.

```bash
uv run --extra local-kernel python -m case_studies.loop_tool_agent.run \
  --live --trusted-local-kernel --attempts 2 --max-turns 2
```

The runner prints the sampled row number, expected answer, selected answer,
turn count, Python tool-call count, and exact-match result. It does not write
live results to disk.

## Full application reference

For the complete parallel implementation, see [Tool-Augmented AI Mathematical](https://github.com/Esabelle11/Tool-Augmented-AI-Mathematical-Reasoning-System)  
[Reasoning System](https://github.com/Esabelle11/Tool-Augmented-AI-Mathematical-Reasoning-System).  
It expands this intentionally small case study into a configurable  
tool-augmented reasoning framework:

```text
Math problem
  → Multiple independent LLM attempts in parallel
  → Native OpenRouter function calling
  → Stateful Jupyter-kernel Python execution
  → Iterative tool feedback and self-correction
  → Answer extraction, voting, and early stopping
```

The full application includes a thread-safe kernel pool, parallel workers,  
configurable attempt and turn budgets, benchmark scripts, runtime tables, and  
consensus aggregation. This case study keeps the same core loop but limits it  
to a small sampled dataset, one local kernel, a strict request budget, and an  
easy-to-audit JSON tool protocol for learning purposes.
