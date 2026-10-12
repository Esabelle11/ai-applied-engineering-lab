# Executable Engineering-Pattern Catalog

Generated from `engineering_patterns/**/pattern.yaml` by `scripts/generate_catalog.py`.
The numbering organizes independent handbook categories; it is not a runtime sequence.

## 01_prompt_engineering

SDK owner(s): `applied_ai.prompting, applied_ai.core.structured`

| Pattern | ID | Offline |
| --- | --- | --- |
| [Sequential prompt chaining](../engineering_patterns/01_prompt_engineering/prompt_chaining/README.md) | `prompt_engineering.prompt_chaining` | Yes |
| [Prompt Templates](../engineering_patterns/01_prompt_engineering/prompt_templates/README.md) | `prompt_engineering.prompt_templates` | Yes |
| [Schema-constrained generation](../engineering_patterns/01_prompt_engineering/structured_outputs/README.md) | `prompt_engineering.structured_outputs` | Yes |

## 02_model_integration

SDK owner(s): `applied_ai.providers, applied_ai.routing, applied_ai.inference`

| Pattern | ID | Offline |
| --- | --- | --- |
| [Concurrent synchronous calls](../engineering_patterns/02_model_integration/async_inference/README.md) | `model_integration.async_inference` | Yes |
| [Basic API Integration](../engineering_patterns/02_model_integration/basic_api_integration/README.md) | `model_integration.basic_api_integration` | Yes |
| [Explicit capability detection](../engineering_patterns/02_model_integration/model_capability_detection/README.md) | `model_integration.model_capability_detection` | Yes |
| [Task-based model routing](../engineering_patterns/02_model_integration/multi_model_routing/README.md) | `model_integration.multi_model_routing` | Yes |

## 03_agent_orchestration

SDK owner(s): `applied_ai.orchestration`

| Pattern | ID | Offline |
| --- | --- | --- |
| [Stateful graph and checkpoint resume](../engineering_patterns/03_agent_orchestration/graph_workflows/README.md) | `agent_orchestration.graph_workflows` | Yes |

## 04_knowledge_and_context

SDK owner(s): `applied_ai.knowledge`

| Pattern | ID | Offline |
| --- | --- | --- |
| [Offline lexical retrieval and grounded prompt](../engineering_patterns/04_knowledge_and_context/rag_pipelines/README.md) | `knowledge_and_context.rag_pipelines` | Yes |

## 05_reliability_engineering

SDK owner(s): `applied_ai.reliability`

| Pattern | ID | Offline |
| --- | --- | --- |
| [Retry backoff policy comparison](../engineering_patterns/05_reliability_engineering/exponential_backoff/README.md) | `reliability_engineering.exponential_backoff` | Yes |
| [Retry, Deadline, and Fallback](../engineering_patterns/05_reliability_engineering/retry_mechanisms/README.md) | `reliability.retry_mechanisms` | Yes |

## 06_evaluation_and_observability

SDK owner(s): `applied_ai.evaluation`

| Pattern | ID | Offline |
| --- | --- | --- |
| [Deterministic evaluation dataset](../engineering_patterns/06_evaluation_and_observability/response_quality/README.md) | `evaluation_and_observability.response_quality` | Yes |

## 07_optimization

SDK owner(s): `applied_ai.optimization`

| Pattern | ID | Offline |
| --- | --- | --- |
| [Request-keyed response caching](../engineering_patterns/07_optimization/response_caching/README.md) | `optimization.response_caching` | Yes |

## 08_reasoning_and_execution

SDK owner(s): `applied_ai.reasoning, applied_ai.execution`

| Pattern | ID | Offline |
| --- | --- | --- |
| [Iterative independent verification](../engineering_patterns/08_reasoning_and_execution/plan_execute_verify/README.md) | `reasoning_and_execution.plan_execute_verify` | Yes |

Run all offline patterns:

```bash
uv run --offline --locked python scripts/run_all_patterns.py
```

Only entries with a runnable manifest are listed; directories in the long-term roadmap are not claimed as implemented.
