# Zero-shot prompting

Builds a provider-neutral system instruction and user task without demonstrations. `build_zero_shot_messages()` validates required text and makes the desired output format explicit; `execute_zero_shot()` performs exactly one provider call.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/01_prompt_engineering/zero_shot_prompting/run.py
```

The example uses `MockProvider`. It does not claim that zero-shot prompts are reliable for every task; evaluate them before using them in a workflow.
