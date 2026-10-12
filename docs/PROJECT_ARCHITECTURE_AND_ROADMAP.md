# Applied AI Engineering Lab

**Architecture, Engineering Patterns & Development Roadmap**  
**Document type:** Project design and implementation plan  
**Status:** Proposed architecture; implementation not yet complete  
**Version:** 1.0  
**Date:** 2026-10-11

---

## 1. Project Overview

**Applied AI Engineering Lab** is a Python-first, framework-independent, executable engineering handbook supported by a reusable software development kit (SDK), testing utilities, controlled experiments, benchmarks, and small reference applications.

Its core purpose is to extract generalizable solutions from prior Applied AI projects and make those solutions **understandable, runnable, testable, comparable, and reusable**.

This is **not** merely a set of independent tutorials, nor an attempt to replace existing LLM gateways, agent frameworks, or vector databases. The aim is to show developers **which pattern to use, how to implement it, how it fails, what its tradeoffs are, and how to verify it**.

### 1.1 Goals

1. Establish a consistent, installable Python interface for common Applied AI capabilities.
2. Organize techniques into eight standalone engineering-pattern categories.
3. Provide runnable examples and automated tests for every published pattern.
4. Support provider/framework alternatives without locking the architecture to one vendor.
5. Introduce reliability measures such as retries, timeouts, backoff, validation, and fallback.
6. Demonstrate secure tool execution and iterative reasoning with a Python sandbox.
7. Measure quality, correctness, latency, token consumption, cost, and recovery behavior.
8. Reuse lessons from existing projects without copying full application repositories.

### 1.2 Non-goals (especially for v0.1)

- Reimplement all functionality of LiteLLM, LangGraph, or other established frameworks.
- Support every LLM provider or vector database from day one.
- Build a production-ready hosted multi-tenant AI platform as the first milestone.
- Implement all eight categories simultaneously.
- Treat a successful API call or an executable code snippet as proof of task correctness.

### 1.3 Guiding principle

> **Learn → Implement → Test → Stress Test → Benchmark → Compare → Reuse**

Each released pattern should complete this cycle proportionately to its risk and complexity.

---

## 2. Conceptual Architecture

The repository separates **educational patterns** from **reusable implementations**, **verification**, and **real-world applications**.

```text
                  +-------------------------------+
                  |   engineering_patterns/       |
                  |   Main executable handbook    |
                  +-------------------------------+
                     |     imports / demonstrates
                     v
                  +-------------------------------+
                  |   src/applied_ai/              |
                  |   Reusable Python SDK         |
                  +-------------------------------+
                     |                 |
            exercised by            used by
                     v                 v
          +------------------+  +--------------------+
          | tests/           |  | case_studies/      |
          | contracts,       |  | smaller reference  |
          | security, etc.   |  | applications       |
          +------------------+  +--------------------+
                     |
                     v
          +-----------------------------------------+
          | experiments/ + benchmarks/              |
          | Controlled comparisons and evidence     |
          +-----------------------------------------+
                     |
                     v
          +-----------------------------------------+
          | apps/playground/ (optional, later)      |
          | Discover, execute, inspect, compare      |
          +-----------------------------------------+
```

**Dependency direction:** the SDK must never depend on `engineering_patterns/`, `case_studies/`, or the playground. Patterns and case studies may import the SDK. Experiments and tests may exercise all of them. The playground should call defined application services, not import example scripts indiscriminately.

### 2.1 Are pattern categories sequential?

**No.** The category prefixes `01` through `08` are navigation labels, **not** a continuous runtime pipeline. Each category is independently learnable and testable, although examples may share SDK utilities or explicitly compose capabilities.

For example:

- **Basic chatbot:** prompt engineering + model integration + reliability.
- **Citizen assistant:** model integration + knowledge/context + tool workflows + evaluation.
- **Math reasoning agent:** model integration + prompting + reasoning/execution, with reliability and evaluation spanning the full workflow.
- **Multi-agent debate:** model integration + agent orchestration + state management + evaluation.

A category can reference a related pattern from another category, but should avoid duplicating its canonical implementation.

---

## 3. Eight Engineering-Pattern Categories

| ID | Category | Responsibility | Initial representative patterns |
|---|---|---|---|
| 01 | Prompt Engineering | Create, control, and evaluate prompts and outputs | Templates, few-shot prompting, chaining, structured output |
| 02 | Model Integration | Access and route across model providers | Provider adapters, streaming, async, capability-aware routing |
| 03 | Agent Orchestration | Control multi-step agent workflows | State, tools, graph flows, handoffs, checkpoint/resume |
| 04 | Knowledge & Context | Retrieve and maintain contextual information | Embeddings, RAG, retrieval, conversation memory, grounding |
| 05 | Reliability Engineering | Handle partial failure safely | Retry, backoff, timeouts, rate limits, fallback, validation |
| 06 | Evaluation & Observability | Understand behavior and measure success | Test datasets, graders, tracing, cost/latency, regression |
| 07 | Optimization | Improve efficiency without losing quality | Cache, concurrency, batching, token/cost-aware routing |
| 08 | Reasoning & Execution | Solve tasks by iterating with tools | Plan–execute–verify, Python sandbox, independent checking |

### 3.1 Source projects and extraction targets

| Prior project | Main reusable pattern | Related capabilities |
|---|---|---|
| Prompt Forge | Prompt Engineering | Template management, prompt optimization, prompt evaluation |
| WhyBuddy | Model Integration | Multi-model calling, provider selection, response normalization |
| Autonomous Debate Ecosystem | Agent Orchestration | Multi-agent coordination, graph-style workflows, state transitions |
| CitizenAssist AI | Knowledge & Context | RAG, vector retrieval, conversational context, structured tools |
| Math Reasoning Project | Reasoning & Execution | Iterative loops, Python execution, verification and feedback |
| Shared concerns across projects | Reliability / Evaluation / Optimization | Retry, timeouts, instrumentation, benchmarks, costs |

The case-study adaptations should be **small and reproducible**. Original product code should not be copied wholesale into the handbook.

---

## 4. Target Repository Structure

> This is the **long-term target**. Empty placeholder directories should not be created merely to make the tree look complete. Build subdirectories when corresponding code and tests are ready.

```text
applied-ai-engineering-lab/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
├── pyproject.toml
├── uv.lock
├── Makefile
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
│
├── engineering_patterns/                   # MAIN EXECUTABLE HANDBOOK
│   ├── README.md
│   ├── _template/
│   │   ├── README.md
│   │   ├── pattern.yaml
│   │   ├── config.yaml
│   │   ├── run.py
│   │   └── tests/
│   │       └── test_pattern.py
│   │
│   ├── 01_prompt_engineering/
│   │   ├── README.md
│   │   ├── prompt_templates/
│   │   ├── zero_shot_prompting/
│   │   ├── few_shot_prompting/
│   │   ├── prompt_chaining/
│   │   ├── structured_outputs/
│   │   ├── dynamic_prompt_construction/
│   │   ├── prompt_versioning/
│   │   ├── prompt_optimization/
│   │   ├── prompt_injection_defense/
│   │   └── prompt_evaluation/
│   │
│   ├── 02_model_integration/
│   │   ├── README.md
│   │   ├── basic_api_integration/
│   │   ├── provider_abstraction/
│   │   ├── model_capability_detection/
│   │   ├── multi_model_routing/
│   │   ├── model_fallback/
│   │   ├── streaming_responses/
│   │   ├── async_inference/
│   │   ├── parallel_model_execution/
│   │   ├── local_model_inference/
│   │   ├── multimodal_input/
│   │   ├── function_calling/
│   │   └── model_response_normalization/
│   │
│   ├── 03_agent_orchestration/
│   │   ├── README.md
│   │   ├── single_agent/
│   │   ├── multi_agent/
│   │   ├── manual_agent_loop/
│   │   ├── state_management/
│   │   ├── graph_workflows/
│   │   ├── sequential_workflows/
│   │   ├── parallel_workflows/
│   │   ├── conditional_routing/
│   │   ├── planner_executor/
│   │   ├── tool_orchestration/
│   │   ├── agent_handoffs/
│   │   ├── human_in_the_loop/
│   │   ├── checkpoint_and_resume/
│   │   └── agent_failure_recovery/
│   │
│   ├── 04_knowledge_and_context/
│   │   ├── README.md
│   │   ├── document_ingestion/
│   │   ├── text_chunking/
│   │   ├── embedding_generation/
│   │   ├── vector_retrieval/
│   │   ├── hybrid_search/
│   │   ├── retrieval_reranking/
│   │   ├── rag_pipelines/
│   │   ├── query_rewriting/
│   │   ├── context_window_management/
│   │   ├── conversation_memory/
│   │   ├── long_term_memory/
│   │   ├── citation_and_grounding/
│   │   └── retrieval_quality/
│   │
│   ├── 05_reliability_engineering/
│   │   ├── README.md
│   │   ├── error_classification/
│   │   ├── retry_mechanisms/
│   │   ├── exponential_backoff/
│   │   ├── jitter_strategies/
│   │   ├── rate_limiting/
│   │   ├── request_queuing/
│   │   ├── timeout_handling/
│   │   ├── circuit_breakers/
│   │   ├── provider_failover/
│   │   ├── output_validation/
│   │   ├── structured_output_recovery/
│   │   ├── idempotency_and_deduplication/
│   │   ├── graceful_degradation/
│   │   └── failure_recovery/
│   │
│   ├── 06_evaluation_and_observability/
│   │   ├── README.md
│   │   ├── evaluation_dataset_design/
│   │   ├── response_quality/
│   │   ├── llm_as_judge/
│   │   ├── agent_evaluation/
│   │   ├── tool_call_evaluation/
│   │   ├── rag_evaluation/
│   │   ├── hallucination_detection/
│   │   ├── latency_benchmarking/
│   │   ├── token_usage_tracking/
│   │   ├── cost_tracking/
│   │   ├── tracing_and_logging/
│   │   ├── regression_testing/
│   │   └── failure_analysis/
│   │
│   ├── 07_optimization/
│   │   ├── README.md
│   │   ├── response_caching/
│   │   ├── semantic_caching/
│   │   ├── request_batching/
│   │   ├── concurrency_control/
│   │   ├── prompt_compression/
│   │   ├── token_optimization/
│   │   ├── context_compression/
│   │   ├── latency_optimization/
│   │   ├── cost_aware_routing/
│   │   └── quality_cost_tradeoffs/
│   │
│   └── 08_reasoning_and_execution/
│       ├── README.md
│       ├── iterative_reasoning/
│       ├── plan_execute_verify/
│       ├── tool_augmented_reasoning/
│       ├── self_correction/
│       ├── reflection_and_critique/
│       ├── code_generation/
│       ├── sandboxed_python_execution/
│       ├── execution_feedback/
│       ├── mathematical_verification/
│       ├── independent_verification/
│       ├── reasoning_budget_control/
│       ├── stopping_conditions/
│       └── execution_failure_recovery/
│
├── src/
│   └── applied_ai/                        # IMPORTABLE PYTHON LIBRARY
│       ├── __init__.py
│       ├── client.py
│       ├── settings.py
│       ├── cli.py
│       ├── core/
│       │   ├── contracts.py
│       │   ├── messages.py
│       │   ├── requests.py
│       │   ├── responses.py
│       │   ├── capabilities.py
│       │   ├── exceptions.py
│       │   └── protocols.py
│       ├── providers/
│       │   ├── base.py
│       │   ├── mock.py
│       │   ├── openai_provider.py
│       │   ├── anthropic_provider.py
│       │   ├── google_provider.py
│       │   ├── openrouter_provider.py
│       │   ├── ollama_provider.py
│       │   └── registry.py
│       ├── prompting/
│       ├── routing/
│       ├── orchestration/
│       ├── knowledge/
│       ├── memory/
│       ├── reliability/
│       ├── execution/
│       ├── evaluation/
│       ├── observability/
│       ├── optimization/
│       ├── security/
│       └── integrations/
│
├── experiments/                           # CONTROLLED COMPARISONS
│   ├── README.md
│   ├── registry/
│   ├── configs/
│   ├── prompting_comparisons/
│   ├── model_comparisons/
│   ├── orchestration_comparisons/
│   ├── retrieval_comparisons/
│   ├── retry_comparisons/
│   ├── reasoning_comparisons/
│   ├── failure_injection/
│   ├── runners/
│   └── results/
│
├── benchmarks/                            # METRICS + REPRODUCIBILITY
│   ├── README.md
│   ├── datasets/
│   │   ├── reasoning/
│   │   ├── retrieval/
│   │   ├── structured_output/
│   │   └── tool_execution/
│   ├── scenarios/
│   │   ├── normal_operation/
│   │   ├── rate_limit_failures/
│   │   ├── provider_outages/
│   │   ├── malformed_outputs/
│   │   └── execution_failures/
│   ├── runners/
│   ├── metrics/
│   ├── reports/
│   └── baselines/
│
├── case_studies/                          # MINIMAL REFERENCE APPLICATIONS
│   ├── README.md
│   ├── autonomous_debate/
│   ├── prompt_forge/
│   ├── whybuddy/
│   ├── citizen_assist/
│   └── math_reasoning/
│
├── apps/
│   └── playground/                        # OPTIONAL LATER-STAGE UI
│       ├── backend/
│       └── frontend/
│
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── end_to_end/
│   ├── security/
│   ├── sandbox/
│   ├── performance/
│   └── smoke/
│
├── infra/
│   ├── docker/
│   ├── sandbox/
│   ├── compose.dev.yaml
│   └── monitoring/
├── configs/
│   ├── providers.example.yaml
│   ├── models.example.yaml
│   ├── retry_policy.yaml
│   ├── cost_limits.yaml
│   ├── sandbox_policy.yaml
│   └── evaluation.yaml
├── docs/
│   ├── getting_started.md
│   ├── installation.md
│   ├── architecture.md
│   ├── pattern_catalog.md
│   ├── sdk_reference.md
│   ├── engineering_principles.md
│   ├── security_model.md
│   ├── benchmarking_guide.md
│   ├── contributing_patterns.md
│   ├── design_decisions/
│   ├── tutorials/
│   └── diagrams/
├── scripts/
│   ├── validate_patterns.py
│   ├── run_pattern.py
│   ├── run_tests.py
│   ├── run_benchmarks.py
│   ├── generate_catalog.py
│   └── check_environment.py
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── PULL_REQUEST_TEMPLATE.md
    └── workflows/
        ├── ci.yml
        ├── lint.yml
        ├── security.yml
        └── documentation.yml
```

**Python packaging note:** folder names beginning with `01_`, `02_`, etc. are fine for handbook organization but should not be used as ordinary Python import package names. Runnable examples can be invoked by path or a pattern runner; reusable imports come from `applied_ai`.

---

## 5. Responsibility and Ownership Rules

| Area | Owns | Does **not** own |
|---|---|---|
| `engineering_patterns/` | Explanations, runnable demonstrations, alternatives, pattern-specific tests, comparison notes | Duplicated canonical SDK logic |
| `src/applied_ai/` | Stable, reusable interfaces and implementations | Tutorial-specific assumptions or UI presentation |
| `experiments/` | Hypotheses, configurations, controlled comparison runs, results | Production library behavior |
| `benchmarks/` | Evaluation datasets, metrics, repeatable scenarios, published measurements | Unverifiable performance claims |
| `case_studies/` | Compositions of patterns in small recognizable applications | Entire original project source trees |
| `tests/` | Contract, unit, integration, security, and regression checks | Manual demonstrations as the only proof of correctness |
| `apps/playground/` | Pattern discovery, execution UI, visual comparison | Sensitive provider keys in browser code; unrestricted sandbox execution |

**Shared-implementation rule:** if retry behavior is used by agent, model, and reasoning modules, implement the reusable policy once under `src/applied_ai/reliability/`, then link to it from each applicable pattern.

---

## 6. Standard for Each Engineering Pattern

A published pattern should be an independently runnable learning unit with a machine-readable manifest.

```text
engineering_patterns/05_reliability_engineering/retry_mechanisms/
├── README.md                       # Problem, concept, usage, tradeoffs
├── pattern.yaml                    # Catalog and execution metadata
├── config.yaml                     # Non-secret example configuration
├── implementations/
│   ├── manual_retry.py
│   ├── tenacity_retry.py
│   └── sdk_retry.py
├── examples/
│   ├── basic_usage.py
│   └── rate_limit_recovery.py
├── tests/
│   └── test_retry_patterns.py
└── comparison.md                   # Evidence, not unsupported rankings
```

### 6.1 Minimum contents of its README

1. **Problem:** What engineering problem does this solve?
2. **Context:** What assumptions and prerequisites apply?
3. **Mechanism:** How does it work, including a flow/diagram when helpful?
4. **Implementation:** How can someone execute it locally?
5. **Alternatives:** What other strategies exist?
6. **Tradeoffs:** What are the quality, latency, cost, complexity, and safety implications?
7. **Failure modes:** What can go wrong, and what should happen then?
8. **Validation:** Which tests and benchmarks support the behavior?
9. **Reuse:** Which SDK interfaces and case studies use this pattern?

### 6.2 Example `pattern.yaml`

```yaml
id: reliability.retry_mechanisms
name: Retry Mechanisms
category: reliability_engineering
status: experimental
level: intermediate

implementations:
  - manual_retry
  - tenacity_retry
  - sdk_retry

capabilities:
  - transient_error_recovery
  - rate_limit_recovery
  - exponential_backoff

requires_api_key: false
supports_offline_testing: true

validation:
  unit_tests: true
  failure_injection: true
  benchmarking: true
```

`pattern.yaml` enables later automation, but **the README remains useful without any custom tooling**.

---

## 7. SDK Interface and Design Principles

### 7.1 Start with small stable contracts

The first common interfaces should cover:

- `Message`: role and content; a model-neutral representation with room for multimodal parts.
- `LLMRequest`: model identifier, messages, optional generation settings, requested capabilities, request metadata.
- `LLMResponse`: normalized text/content, finish reason, provider/model identity, usage, timing, request ID when available.
- `Provider`: sync and/or async generation capability, with explicit optional streaming/tool/structured-output capabilities.
- `LLMError`: categorized failures that reliability policies can act upon.

Provider differences must **not** be silently erased. For example, unsupported tools or structured output should return a clear capability error or follow an explicitly selected downgrade policy.

### 7.2 Provider implementation sequence

1. `MockProvider` for deterministic, offline tests.
2. One real provider (OpenAI is a reasonable initial choice, but the abstraction should not depend on it).
3. A second distinct provider to test actual portability.
4. Optional OpenAI-compatible provider/OpenRouter and local Ollama adapter.
5. More providers only when they add a demonstrable use case.

### 7.3 Sync, async, and streaming

Start with **simple synchronous generation** to validate contracts. Add async and streaming behind explicit capabilities and contract tests. Avoid imposing a single interface that claims all providers support identical streaming/tool behavior.

### 7.4 Reliability design constraints

- Retry only errors known to be transient; 401/403, invalid configuration, and invalid user requests usually require correction.
- Use bounded attempts, backoff with jitter, and respect `Retry-After` where relevant.
- Define **total request time budgets**, not only per-attempt timeouts.
- Avoid duplicate retries in both provider SDKs and the Lab's reliability wrapper.
- Avoid retrying non-idempotent tool side effects without deduplication or another safe mechanism.
- Treat fallback as an explicit policy: alternative models may differ in tools, JSON schema support, context window, price, and output quality.
- Emit useful traces and redact secrets or sensitive data.

### 7.5 Security of Python execution

The math-reasoning sandbox must be an **isolated execution service or worker**, not an `exec()` call in the application process. It should have, as appropriate to the threat model:

- Strong process isolation and an unprivileged runtime.
- Network disabled by default; allowlisting only with a clear need.
- Read-only filesystem by default and constrained temporary storage.
- CPU, memory, process-count, output-size, and execution-time limits.
- No host credentials, API keys, SSH agent, or cloud metadata access.
- Input and output validation; isolation-focused adversarial testing.
- Separate policies for trusted local demonstrations versus arbitrary user-generated code.

Containerization alone is **not** sufficient protection for hostile untrusted code without appropriate configuration and hardening.

---

## 8. Development Roadmap

The following phases describe **implementation order**, not the runtime order of pattern categories. Validation begins early; Phase 5 expands it into systematic comparisons.

### Phase 0 — Foundation and Repository Setup

**Objective:** establish a clean, installable, testable Python project.

**Work items**

- [ ] Initialize Git repository, `README.md`, license, `.gitignore`, `.env.example`.
- [ ] Create `pyproject.toml`, `uv.lock`, package metadata, and optional dependency groups.
- [ ] Create minimal `src/applied_ai/` package with explicit exports.
- [ ] Create eight category README files and the shared pattern template.
- [ ] Configure linting, formatting, type checking, pytest, and CI.
- [ ] Create mock fixtures, no-secret configuration, and a local test command.
- [ ] Document minimum supported Python version, setup, and development commands.

**Deliverable D0:** package installs in a clean environment; offline tests and CI pass.

**Exit criteria**

- A fresh contributor can install the project following README instructions.
- `import applied_ai` succeeds.
- At least one deterministic test passes with no network/API credentials.
- No secrets are committed.

### Phase 1 — Core LLM Interface

**Objective:** expose a usable provider-neutral generation interface.

**Work items**

- [ ] Define message/request/response contracts and provider exceptions.
- [ ] Implement `MockProvider` with deterministic responses and configurable faults.
- [ ] Implement the first live-provider adapter.
- [ ] Support one straightforward sync `generate()` operation.
- [ ] Add normalized usage/latency metadata when provided by the backend.
- [ ] Add basic structured-output handling with explicit capability checks.
- [ ] Write provider contract and mocked HTTP tests.
- [ ] Publish a `basic_api_integration` runnable pattern.

**Deliverable D1:** the same small example can use the mock and a live provider via the common API.

**Exit criteria**

- Offline sample produces an expected response deterministically.
- Live smoke test is optional, opt-in, and skipped without credentials.
- Unsupported capability requests are rejected or explicitly downgraded.
- Provider-specific exceptions are normalized into documented categories.

### Phase 2 — Reliability Foundation

**Objective:** make LLM requests resilient under realistic, controlled failure conditions.

**Work items**

- [ ] Classify failures: rate limit, transient server error, timeout, authentication, validation, non-retryable client error.
- [ ] Implement bounded retries, exponential backoff, jitter, and `Retry-After` handling.
- [ ] Implement timeouts plus a total request deadline.
- [ ] Introduce configurable local rate limiting and bounded concurrency.
- [ ] Implement explicit model/provider fallback with capability checks.
- [ ] Introduce optional circuit breaker and structured-output validation.
- [ ] Record attempt count, latency, errors, tokens, and cost when measurable.
- [ ] Write deterministic fault-injection tests for 429, 5xx, timeout, malformed response, and exhaustion.

**Deliverable D2:** reliability patterns are executable and tested under injected failures.

**Exit criteria**

- Retryable failures recover within configured limits.
- Non-retryable failures do not loop unnecessarily.
- Retry attempts respect limits and deadlines.
- Tests confirm no duplicate side effects in a representative tool scenario.

### Phase 3 — Engineering-Pattern Library

**Objective:** populate categories incrementally with quality-controlled runnable material.

**Suggested development order** *(this is a scheduling recommendation, not a runtime dependency)*:

1. **02 Model Integration:** basic calling, routing, streaming, async, provider differences.
2. **01 Prompt Engineering:** templates, structured responses, prompt chaining, evaluation.
3. **05 Reliability Engineering:** expand Phase 2 into comparison patterns.
4. **03 Agent Orchestration:** manual loops, state, graph workflows, tools, checkpointing.
5. **04 Knowledge & Context:** ingestion, embeddings, retrieval, RAG, memory, grounding.
6. **08 Reasoning & Execution:** reasoning loops, restricted Python execution, verification.
7. **06 Evaluation & Observability:** reusable evaluation/trace patterns and reporting.
8. **07 Optimization:** caching, batching, concurrency, token/cost optimization.

These submodules can be developed in parallel **after** their shared interface contracts are stable.

**Work items for each published pattern**

- [ ] Implement at least one runnable example.
- [ ] Provide a clear README and `pattern.yaml`.
- [ ] Add tests and representative failure cases.
- [ ] Document assumptions, alternatives, and known limitations.
- [ ] Link to canonical SDK APIs instead of duplicating implementation.
- [ ] Include reproducible comparison evidence when making performance claims.

**Deliverable D3:** a curated set of functioning patterns across the categories; no requirement to fill every planned subdirectory.

**Exit criteria**

- Every published pattern passes `validate_patterns.py`.
- Every published example can run in its declared environment.
- Offline alternatives exist where possible; live execution clearly describes costs and prerequisites.

### Phase 4 — Case Study Extraction

**Objective:** show combinations of patterns solving realistic tasks.

**Work items**

- [ ] Build simplified Prompt Forge reference using prompt templates and evaluation.
- [ ] Build simplified WhyBuddy reference using model abstraction and routing.
- [ ] Build simplified Autonomous Debate reference using multi-agent state and workflows.
- [ ] Build simplified CitizenAssist reference using RAG and grounding.
- [ ] Build simplified Math Reasoning reference using sandbox execution and verification.
- [ ] Write architecture maps showing which engineering patterns each case study composes.

**Deliverable D4:** five small, clearly documented case studies that consume the SDK.

**Exit criteria**

- Shared capabilities come from `src/applied_ai`, not copied implementations.
- Each case study has at least one automated test and a clear run command.
- Synthetic/sample data are used where personal or proprietary data are not needed.

### Phase 5 — Controlled Experiments and Benchmarks

**Objective:** replace anecdotal claims with repeatable evidence.

**Work items**

- [ ] Define experiment manifests: question, controls, inputs, metrics, versioned configurations.
- [ ] Create small, representative datasets and deterministic failure scenarios.
- [ ] Benchmark retry strategies under identical fault sequences.
- [ ] Compare manual orchestration with framework-based orchestration on matched tasks.
- [ ] Compare direct answer, tool-execution, and verification-loop strategies on math tasks.
- [ ] Record answer correctness, tool success, latency (including p50/p95), usage, cost, and error rate where applicable.
- [ ] Save run metadata: model, version, prompt, seed where supported, concurrency, date, environment.
- [ ] Publish both positive and negative findings with sample sizes and limitations.

**Deliverable D5:** reproducible experiment reports; comparisons are explicitly bounded by their tested conditions.

**Exit criteria**

- Another developer can reproduce the offline benchmarks.
- External-provider comparisons state which variability is not controlled.
- Claims are traceable to data and configuration, rather than subjective impressions.

### Phase 6 — Optional Interactive Playground

**Objective:** make the handbook more approachable without changing its core APIs.

**Work items**

- [ ] Provide an API endpoint for pattern discovery and metadata.
- [ ] Allow users to select examples and safely adjust supported parameters.
- [ ] Display inputs, outputs, retries, traces, costs, and validation results.
- [ ] Support side-by-side comparison of compatible implementations.
- [ ] Add authentication/access control where necessary, usage budgets, and restricted execution policies.
- [ ] Ensure generated code is never executed in the web server process.

**Deliverable D6:** optional UI backed by existing SDK and pattern runner interfaces.

**Exit criteria**

- All displayed examples run through defined backend boundaries.
- Secrets are server-side only.
- Sandbox permissions and budget limits are enforced.
- CLI and Python usage remain fully functional without the playground.

### Phase 7 — Documentation and Release

**Objective:** make the project understandable, installable, and safe to contribute to.

**Work items**

- [ ] Finalize SDK public API, versioning, and release notes.
- [ ] Document architectural decisions and backwards-compatibility expectations.
- [ ] Generate/update pattern catalog and API reference.
- [ ] Ensure a green CI suite for the supported Python versions.
- [ ] Complete dependency and secret scans plus sandbox security review.
- [ ] Add contribution template for new patterns and benchmark submissions.
- [ ] Tag the first release after scope/exit criteria are met.

**Deliverable D7:** reproducible, documented first release.

---

## 9. Milestones and Minimum Viable Release

| Milestone | Scope | Required proof |
|---|---|---|
| M0 | Installable skeleton | Local installation + offline CI |
| M1 | Provider abstraction | Mock and one real provider through same request contract |
| M2 | Reliability foundation | Reproducible retry/timeout/fallback fault tests |
| M3 | First three polished patterns | Runnable docs, validation, comparisons for integration + reliability + prompting |
| M4 | One composed reference application | Demonstrates multiple patterns without code duplication |
| M5 | First benchmark report | Reproducible metrics, controls, limitations |

**Recommended v0.1 scope:** M0–M3, with **one small reference case study** and **one benchmark** if feasible. Do not delay v0.1 to complete all planned categories or the playground.

### 9.1 First runnable vertical slice

```text
applied-ai-engineering-lab/
├── pyproject.toml
├── README.md
├── .env.example
├── src/applied_ai/
│   ├── __init__.py
│   ├── core/
│   │   ├── messages.py
│   │   ├── requests.py
│   │   ├── responses.py
│   │   ├── protocols.py
│   │   └── exceptions.py
│   └── providers/
│       ├── mock.py
│       └── openai_provider.py
├── engineering_patterns/
│   ├── 01_prompt_engineering/
│   │   └── basic_prompt/
│   │       ├── README.md
│   │       └── run.py
│   ├── 02_model_integration/
│   ├── 03_agent_orchestration/
│   ├── 04_knowledge_and_context/
│   ├── 05_reliability_engineering/
│   ├── 06_evaluation_and_observability/
│   ├── 07_optimization/
│   └── 08_reasoning_and_execution/
└── tests/
    ├── test_provider_contract.py
    └── test_basic_prompt.py
```

The initial `basic_prompt/run.py` should work using the mock backend **without credentials**. Live model usage is an optional integration test, not a prerequisite for developer onboarding.

---

## 10. Testing and Verification Strategy

| Test type | Focus | Runs offline by default? |
|---|---|---|
| Unit | Parsing, routing, retry rules, budgets, state transitions | Yes |
| Contract | All providers honor common request/response semantics | Yes, with mocks |
| Integration | SDK adapters with controlled fake services | Yes |
| Live-provider smoke | Real API interoperability and configuration | No; explicit opt-in |
| Failure injection | 429, 5xx, timeouts, malformed outputs, partial tool failures | Yes |
| Security | Secrets, untrusted inputs, sandbox constraints | Yes where feasible |
| End-to-end | Small case-study outcomes | Prefer mock fixtures |
| Benchmark | Reliability, latency, usage, task outcomes | Offline baseline + optional live |

### 10.1 Minimum quality gate for a new pattern

- Documentation and prerequisites are complete.
- The example has one documented command to run.
- Normal behavior and at least one relevant failure path have tests.
- Its SDK dependency is explicit.
- External credentials and paid API usage are never assumed silently.
- Outputs are deterministic when the test is intended to be deterministic.
- Any score, accuracy, speed, or cost comparison includes measurement context.

---

## 11. Experiment Reporting Standard

Every serious comparison should define:

1. **Question and hypothesis:** What engineering tradeoff is being evaluated?
2. **Alternatives and controls:** Which implementations are compared?
3. **Input distribution:** Which datasets and failure profiles are used?
4. **Environment:** Package versions, providers/models, concurrency, hardware, and dates.
5. **Metrics:** Accuracy/task success, p50/p95 latency, retry count, cost, error rate, resource use.
6. **Statistical caution:** Sample sizes, variance, uncertainty, and external-provider nondeterminism.
7. **Decision:** Under what conditions is each option preferable?
8. **Limitations:** What the study cannot establish.

For LLM-as-judge evaluations, treat the judge as an imperfect instrument. Use deterministic checks or human-reviewed samples where appropriate; avoid presenting judge scores as ground truth.

---

## 12. Operational and Security Requirements

### Secrets and privacy

- Never commit API keys, `.env`, proprietary documents, or production conversation logs.
- Use anonymized/synthetic fixtures for publicly distributable case studies.
- Redact sensitive request data from logs; make prompt-content logging optional.

### Runtime safety

- Require bounded concurrency, request budgets, and maximum cost settings for live examples.
- Track/restrict tool side effects; demonstrate idempotency for actions that change state.
- Restrict arbitrary code execution to the isolated sandbox with audited policies.
- Mark intentionally insecure examples clearly and keep them out of default runnable paths.

### Dependency discipline

- Keep provider adapters, vector stores, agent frameworks, and playground libraries as optional extras where possible.
- Pin/lock reproducible development environments and update dependencies deliberately.
- Keep installation for the simple mock example lightweight.

---

## 13. Definition of Done

A repository release is ready when:

- [ ] A fresh developer can install it and run at least one complete pattern offline.
- [ ] The shared SDK exposes documented, tested contracts.
- [ ] The live-provider flow works through the same interface when credentials are supplied.
- [ ] Reliability behavior is tested with injected failures, bounded retries, and deadlines.
- [ ] Published patterns have READMEs, examples, tests, and known limitations.
- [ ] At least one case study composes multiple patterns without copying shared code.
- [ ] Benchmark claims are reproducible and appropriately qualified.
- [ ] CI passes; secrets are absent; security boundaries are documented.

**Future maturity indicators:** meaningful external reuse, reproducible third-party benchmarks, contributor adoption, documented compatibility, and stable SDK interfaces. Repository size or number of examples alone is not evidence of quality.

---

## 14. Immediate Next Action

**Begin with Phase 0 and a narrow slice of Phase 1:**

1. Create the Python package and basic quality-tooling setup.
2. Define request/response and provider contracts.
3. Implement a deterministic mock model backend.
4. Publish a single executable basic-prompt pattern.
5. Verify local installation, tests, and CI.

**Do not** start by implementing all eight pattern categories, creating a UI, or building an unrestricted Python execution system. The best first milestone is a small, complete example whose contracts and testing practices can scale to the rest of the handbook.

---

*This document is a project architecture and development reference. It describes proposed work and acceptance criteria; it is not an instruction prompt for a coding agent and does not claim any implementation is already complete.*
