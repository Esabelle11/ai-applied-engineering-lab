# Phase 4 — Case Study Architecture Maps

The five independent reference applications demonstrate composition of reusable patterns. **None are a copy of the original application**. Only `src/applied_ai` owns shared implementation code.

## 1. Prompt Forge

```text
Synthetic EvalCase[]
    |                 +-> PromptTemplate (01)
    +-> variant prompts +-> LLMProvider.generate (02)
                             |
                             v
                         evaluate (06) -> exact-match report
```

## 2. WhyBuddy

```text
.env -> ProviderFactory (02) -> LLMProvider (02)
            |                     ^
            +-> TaskRouter (02) --+  (quick vs detailed ModelTarget)
                                  |
                           LLMResponse (02)
```

## 3. Autonomous Debate Ecosystem

```text
Topic -> GraphSnapshot (03) -> opening (03 + 02)
                                  -> optimist (03 + 02)
                                  -> CHECKPOINT (03)
                                  -> skeptic (03 + 02)
                                  -> synthesis (03 + 02)
                                  -> END
```

## 4. CitizenAssist AI

```text
Synthetic documents -> LexicalRetriever (04)
                           |
Question -> answer_with_context (04) -> LLMProvider (02)
                           |
                           v
                    Citation-ID checks
```

## 5. Math Reasoning

```text
Question -> VerificationLoop (08 + 02) -> independent numeric oracle (08)
                         |
                  --sandbox opt-in
                         v
                 DockerPythonSandbox (08)
                         |
                 stdout + exit status
                         v
                 independent verification
```

**Cross-cutting note:** Reliability from Phase 2 can be composed via `ReliableProvider` (05); the Phase 4 demonstrations do not implicitly retry billable requests. All examples are deterministic with mock providers, except explicit external Docker execution and live-model invocations. For a production system, consider human-in-the-loop validation, budgets, tracing, domain-specific evaluation, persistent state, and secure infrastructure.
