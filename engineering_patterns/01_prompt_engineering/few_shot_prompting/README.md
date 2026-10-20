# Few-shot prompting

Defines validated `Example` records and renders each demonstration inside an explicit XML-like boundary before presenting a new query. The delimiters make the example/input relationship inspectable and reduce accidental ambiguity.

Run offline:

```bash
uv run --offline --locked python engineering_patterns/01_prompt_engineering/few_shot_prompting/run.py
```

Examples can steer a model but consume context and may overfit it to the demonstrated format.
