# Executable Engineering-Pattern Catalog

Generated from `engineering_patterns/**/pattern.yaml` by `scripts/generate_catalog.py`.
The numbering organizes independent handbook categories; it is not a runtime sequence.

## 01_prompt_engineering

SDK owner(s): `applied_ai.prompting, applied_ai.core.structured`

| Pattern | ID | Started | Offline |
| --- | --- | --- | --- |
| [Dynamic Prompt Construction](../engineering_patterns/01_prompt_engineering/dynamic_prompt_construction/README.md) | `prompt_engineering.dynamic_prompt_construction` | 15/10/2026 | Yes |
| [Few Shot Prompting](../engineering_patterns/01_prompt_engineering/few_shot_prompting/README.md) | `prompt_engineering.few_shot_prompting` | 15/10/2026 | Yes |
| [Sequential prompt chaining](../engineering_patterns/01_prompt_engineering/prompt_chaining/README.md) | `prompt_engineering.prompt_chaining` | 11/10/2026 | Yes |
| [Prompt Evaluation](../engineering_patterns/01_prompt_engineering/prompt_evaluation/README.md) | `prompt_engineering.prompt_evaluation` | 15/10/2026 | Yes |
| [Prompt Injection Defense](../engineering_patterns/01_prompt_engineering/prompt_injection_defense/README.md) | `prompt_engineering.prompt_injection_defense` | 15/10/2026 | Yes |
| [Prompt Optimization](../engineering_patterns/01_prompt_engineering/prompt_optimization/README.md) | `prompt_engineering.prompt_optimization` | 15/10/2026 | Yes |
| [Prompt Templates](../engineering_patterns/01_prompt_engineering/prompt_templates/README.md) | `prompt_engineering.prompt_templates` | 11/10/2026 | Yes |
| [Prompt Versioning](../engineering_patterns/01_prompt_engineering/prompt_versioning/README.md) | `prompt_engineering.prompt_versioning` | 15/10/2026 | Yes |
| [Schema-constrained generation](../engineering_patterns/01_prompt_engineering/structured_outputs/README.md) | `prompt_engineering.structured_outputs` | 11/10/2026 | Yes |
| [Zero Shot Prompting](../engineering_patterns/01_prompt_engineering/zero_shot_prompting/README.md) | `prompt_engineering.zero_shot_prompting` | 15/10/2026 | Yes |

## 02_model_integration

SDK owner(s): `applied_ai.providers, applied_ai.routing, applied_ai.inference`

| Pattern | ID | Started | Offline |
| --- | --- | --- | --- |
| [Concurrent synchronous calls](../engineering_patterns/02_model_integration/async_inference/README.md) | `model_integration.async_inference` | 11/10/2026 | Yes |
| [Basic API Integration](../engineering_patterns/02_model_integration/basic_api_integration/README.md) | `model_integration.basic_api_integration` | 11/10/2026 | Yes |
| [Function Calling](../engineering_patterns/02_model_integration/function_calling/README.md) | `model_integration.function_calling` | 15/10/2026 | Yes |
| [Local Model Inference](../engineering_patterns/02_model_integration/local_model_inference/README.md) | `model_integration.local_model_inference` | 15/10/2026 | Yes |
| [Explicit capability detection](../engineering_patterns/02_model_integration/model_capability_detection/README.md) | `model_integration.model_capability_detection` | 11/10/2026 | Yes |
| [Model Response Normalization](../engineering_patterns/02_model_integration/model_response_normalization/README.md) | `model_integration.model_response_normalization` | 15/10/2026 | Yes |
| [Task-based model routing](../engineering_patterns/02_model_integration/multi_model_routing/README.md) | `model_integration.multi_model_routing` | 11/10/2026 | Yes |
| [Multimodal Input](../engineering_patterns/02_model_integration/multimodal_input/README.md) | `model_integration.multimodal_input` | 15/10/2026 | Yes |
| [Parallel Model Execution](../engineering_patterns/02_model_integration/parallel_model_execution/README.md) | `model_integration.parallel_model_execution` | 15/10/2026 | Yes |
| [Provider Abstraction](../engineering_patterns/02_model_integration/provider_abstraction/README.md) | `model_integration.provider_abstraction` | 15/10/2026 | Yes |
| [Streaming Responses](../engineering_patterns/02_model_integration/streaming_responses/README.md) | `model_integration.streaming_responses` | 15/10/2026 | Yes |

## 03_agent_orchestration

SDK owner(s): `applied_ai.orchestration`

| Pattern | ID | Started | Offline |
| --- | --- | --- | --- |
| [Agent Failure Recovery](../engineering_patterns/03_agent_orchestration/agent_failure_recovery/README.md) | `agent_orchestration.agent_failure_recovery` | 15/10/2026 | Yes |
| [Agent Handoffs](../engineering_patterns/03_agent_orchestration/agent_handoffs/README.md) | `agent_orchestration.agent_handoffs` | 15/10/2026 | Yes |
| [Checkpoint And Resume](../engineering_patterns/03_agent_orchestration/checkpoint_and_resume/README.md) | `agent_orchestration.checkpoint_and_resume` | 15/10/2026 | Yes |
| [Conditional Routing](../engineering_patterns/03_agent_orchestration/conditional_routing/README.md) | `agent_orchestration.conditional_routing` | 15/10/2026 | Yes |
| [Stateful graph and checkpoint resume](../engineering_patterns/03_agent_orchestration/graph_workflows/README.md) | `agent_orchestration.graph_workflows` | 11/10/2026 | Yes |
| [Human In The Loop](../engineering_patterns/03_agent_orchestration/human_in_the_loop/README.md) | `agent_orchestration.human_in_the_loop` | 15/10/2026 | Yes |
| [Manual Agent Loop](../engineering_patterns/03_agent_orchestration/manual_agent_loop/README.md) | `agent_orchestration.manual_agent_loop` | 15/10/2026 | Yes |
| [Multi Agent](../engineering_patterns/03_agent_orchestration/multi_agent/README.md) | `agent_orchestration.multi_agent` | 15/10/2026 | Yes |
| [Parallel Workflows](../engineering_patterns/03_agent_orchestration/parallel_workflows/README.md) | `agent_orchestration.parallel_workflows` | 15/10/2026 | Yes |
| [Planner Executor](../engineering_patterns/03_agent_orchestration/planner_executor/README.md) | `agent_orchestration.planner_executor` | 15/10/2026 | Yes |
| [Sequential Workflows](../engineering_patterns/03_agent_orchestration/sequential_workflows/README.md) | `agent_orchestration.sequential_workflows` | 15/10/2026 | Yes |
| [Single Agent](../engineering_patterns/03_agent_orchestration/single_agent/README.md) | `agent_orchestration.single_agent` | 15/10/2026 | Yes |
| [State Management](../engineering_patterns/03_agent_orchestration/state_management/README.md) | `agent_orchestration.state_management` | 15/10/2026 | Yes |
| [Tool Orchestration](../engineering_patterns/03_agent_orchestration/tool_orchestration/README.md) | `agent_orchestration.tool_orchestration` | 15/10/2026 | Yes |

## 04_knowledge_and_context

SDK owner(s): `applied_ai.knowledge`

| Pattern | ID | Started | Offline |
| --- | --- | --- | --- |
| [Citation And Grounding](../engineering_patterns/04_knowledge_and_context/citation_and_grounding/README.md) | `knowledge_and_context.citation_and_grounding` | 15/10/2026 | Yes |
| [Context Window Management](../engineering_patterns/04_knowledge_and_context/context_window_management/README.md) | `knowledge_and_context.context_window_management` | 15/10/2026 | Yes |
| [Conversation Memory](../engineering_patterns/04_knowledge_and_context/conversation_memory/README.md) | `knowledge_and_context.conversation_memory` | 15/10/2026 | Yes |
| [Document Ingestion](../engineering_patterns/04_knowledge_and_context/document_ingestion/README.md) | `knowledge_and_context.document_ingestion` | 15/10/2026 | Yes |
| [Embedding Generation](../engineering_patterns/04_knowledge_and_context/embedding_generation/README.md) | `knowledge_and_context.embedding_generation` | 15/10/2026 | Yes |
| [Hybrid Search](../engineering_patterns/04_knowledge_and_context/hybrid_search/README.md) | `knowledge_and_context.hybrid_search` | 15/10/2026 | Yes |
| [Long Term Memory](../engineering_patterns/04_knowledge_and_context/long_term_memory/README.md) | `knowledge_and_context.long_term_memory` | 15/10/2026 | Yes |
| [Query Rewriting](../engineering_patterns/04_knowledge_and_context/query_rewriting/README.md) | `knowledge_and_context.query_rewriting` | 15/10/2026 | Yes |
| [Offline lexical retrieval and grounded prompt](../engineering_patterns/04_knowledge_and_context/rag_pipelines/README.md) | `knowledge_and_context.rag_pipelines` | 11/10/2026 | Yes |
| [Retrieval Quality](../engineering_patterns/04_knowledge_and_context/retrieval_quality/README.md) | `knowledge_and_context.retrieval_quality` | 15/10/2026 | Yes |
| [Retrieval Reranking](../engineering_patterns/04_knowledge_and_context/retrieval_reranking/README.md) | `knowledge_and_context.retrieval_reranking` | 15/10/2026 | Yes |
| [Text Chunking](../engineering_patterns/04_knowledge_and_context/text_chunking/README.md) | `knowledge_and_context.text_chunking` | 15/10/2026 | Yes |
| [Vector Retrieval](../engineering_patterns/04_knowledge_and_context/vector_retrieval/README.md) | `knowledge_and_context.vector_retrieval` | 15/10/2026 | Yes |

## 05_reliability_engineering

SDK owner(s): `applied_ai.reliability`

| Pattern | ID | Started | Offline |
| --- | --- | --- | --- |
| [Circuit Breakers](../engineering_patterns/05_reliability_engineering/circuit_breakers/README.md) | `reliability_engineering.circuit_breakers` | 15/10/2026 | Yes |
| [Error Classification](../engineering_patterns/05_reliability_engineering/error_classification/README.md) | `reliability_engineering.error_classification` | 15/10/2026 | Yes |
| [Retry backoff policy comparison](../engineering_patterns/05_reliability_engineering/exponential_backoff/README.md) | `reliability_engineering.exponential_backoff` | 11/10/2026 | Yes |
| [Failure Recovery](../engineering_patterns/05_reliability_engineering/failure_recovery/README.md) | `reliability_engineering.failure_recovery` | 15/10/2026 | Yes |
| [Graceful Degradation](../engineering_patterns/05_reliability_engineering/graceful_degradation/README.md) | `reliability_engineering.graceful_degradation` | 15/10/2026 | Yes |
| [Idempotency And Deduplication](../engineering_patterns/05_reliability_engineering/idempotency_and_deduplication/README.md) | `reliability_engineering.idempotency_and_deduplication` | 15/10/2026 | Yes |
| [Jitter Strategies](../engineering_patterns/05_reliability_engineering/jitter_strategies/README.md) | `reliability_engineering.jitter_strategies` | 15/10/2026 | Yes |
| [Output Validation](../engineering_patterns/05_reliability_engineering/output_validation/README.md) | `reliability_engineering.output_validation` | 15/10/2026 | Yes |
| [Provider Failover](../engineering_patterns/05_reliability_engineering/provider_failover/README.md) | `reliability_engineering.provider_failover` | 15/10/2026 | Yes |
| [Rate Limiting](../engineering_patterns/05_reliability_engineering/rate_limiting/README.md) | `reliability_engineering.rate_limiting` | 15/10/2026 | Yes |
| [Request Queuing](../engineering_patterns/05_reliability_engineering/request_queuing/README.md) | `reliability_engineering.request_queuing` | 15/10/2026 | Yes |
| [Retry, Deadline, and Fallback](../engineering_patterns/05_reliability_engineering/retry_mechanisms/README.md) | `reliability.retry_mechanisms` | 11/10/2026 | Yes |
| [Structured Output Recovery](../engineering_patterns/05_reliability_engineering/structured_output_recovery/README.md) | `reliability_engineering.structured_output_recovery` | 15/10/2026 | Yes |
| [Timeout Handling](../engineering_patterns/05_reliability_engineering/timeout_handling/README.md) | `reliability_engineering.timeout_handling` | 15/10/2026 | Yes |

## 06_evaluation_and_observability

SDK owner(s): `applied_ai.evaluation`

| Pattern | ID | Started | Offline |
| --- | --- | --- | --- |
| [Agent Evaluation](../engineering_patterns/06_evaluation_and_observability/agent_evaluation/README.md) | `evaluation_and_observability.agent_evaluation` | 15/10/2026 | Yes |
| [Cost Tracking](../engineering_patterns/06_evaluation_and_observability/cost_tracking/README.md) | `evaluation_and_observability.cost_tracking` | 15/10/2026 | Yes |
| [Evaluation Dataset Design](../engineering_patterns/06_evaluation_and_observability/evaluation_dataset_design/README.md) | `evaluation_and_observability.evaluation_dataset_design` | 15/10/2026 | Yes |
| [Failure Analysis](../engineering_patterns/06_evaluation_and_observability/failure_analysis/README.md) | `evaluation_and_observability.failure_analysis` | 15/10/2026 | Yes |
| [Hallucination Detection](../engineering_patterns/06_evaluation_and_observability/hallucination_detection/README.md) | `evaluation_and_observability.hallucination_detection` | 15/10/2026 | Yes |
| [Latency Benchmarking](../engineering_patterns/06_evaluation_and_observability/latency_benchmarking/README.md) | `evaluation_and_observability.latency_benchmarking` | 15/10/2026 | Yes |
| [Llm As Judge](../engineering_patterns/06_evaluation_and_observability/llm_as_judge/README.md) | `evaluation_and_observability.llm_as_judge` | 15/10/2026 | Yes |
| [Rag Evaluation](../engineering_patterns/06_evaluation_and_observability/rag_evaluation/README.md) | `evaluation_and_observability.rag_evaluation` | 15/10/2026 | Yes |
| [Regression Testing](../engineering_patterns/06_evaluation_and_observability/regression_testing/README.md) | `evaluation_and_observability.regression_testing` | 15/10/2026 | Yes |
| [Deterministic evaluation dataset](../engineering_patterns/06_evaluation_and_observability/response_quality/README.md) | `evaluation_and_observability.response_quality` | 11/10/2026 | Yes |
| [Token Usage Tracking](../engineering_patterns/06_evaluation_and_observability/token_usage_tracking/README.md) | `evaluation_and_observability.token_usage_tracking` | 15/10/2026 | Yes |
| [Tool Call Evaluation](../engineering_patterns/06_evaluation_and_observability/tool_call_evaluation/README.md) | `evaluation_and_observability.tool_call_evaluation` | 15/10/2026 | Yes |
| [Tracing And Logging](../engineering_patterns/06_evaluation_and_observability/tracing_and_logging/README.md) | `evaluation_and_observability.tracing_and_logging` | 15/10/2026 | Yes |

## 07_optimization

SDK owner(s): `applied_ai.optimization`

| Pattern | ID | Started | Offline |
| --- | --- | --- | --- |
| [Concurrency Control](../engineering_patterns/07_optimization/concurrency_control/README.md) | `optimization.concurrency_control` | 15/10/2026 | Yes |
| [Context Compression](../engineering_patterns/07_optimization/context_compression/README.md) | `optimization.context_compression` | 15/10/2026 | Yes |
| [Cost Aware Routing](../engineering_patterns/07_optimization/cost_aware_routing/README.md) | `optimization.cost_aware_routing` | 15/10/2026 | Yes |
| [Latency Optimization](../engineering_patterns/07_optimization/latency_optimization/README.md) | `optimization.latency_optimization` | 15/10/2026 | Yes |
| [Prompt Compression](../engineering_patterns/07_optimization/prompt_compression/README.md) | `optimization.prompt_compression` | 15/10/2026 | Yes |
| [Quality Cost Tradeoffs](../engineering_patterns/07_optimization/quality_cost_tradeoffs/README.md) | `optimization.quality_cost_tradeoffs` | 15/10/2026 | Yes |
| [Request Batching](../engineering_patterns/07_optimization/request_batching/README.md) | `optimization.request_batching` | 15/10/2026 | Yes |
| [Request-keyed response caching](../engineering_patterns/07_optimization/response_caching/README.md) | `optimization.response_caching` | 11/10/2026 | Yes |
| [Semantic Caching](../engineering_patterns/07_optimization/semantic_caching/README.md) | `optimization.semantic_caching` | 15/10/2026 | Yes |
| [Token Optimization](../engineering_patterns/07_optimization/token_optimization/README.md) | `optimization.token_optimization` | 15/10/2026 | Yes |

## 08_reasoning_and_execution

SDK owner(s): `applied_ai.reasoning, applied_ai.execution`

| Pattern | ID | Started | Offline |
| --- | --- | --- | --- |
| [Code Generation](../engineering_patterns/08_reasoning_and_execution/code_generation/README.md) | `reasoning_and_execution.code_generation` | 15/10/2026 | Yes |
| [Execution Failure Recovery](../engineering_patterns/08_reasoning_and_execution/execution_failure_recovery/README.md) | `reasoning_and_execution.execution_failure_recovery` | 15/10/2026 | Yes |
| [Execution Feedback](../engineering_patterns/08_reasoning_and_execution/execution_feedback/README.md) | `reasoning_and_execution.execution_feedback` | 15/10/2026 | Yes |
| [Independent Verification](../engineering_patterns/08_reasoning_and_execution/independent_verification/README.md) | `reasoning_and_execution.independent_verification` | 15/10/2026 | Yes |
| [Iterative Reasoning](../engineering_patterns/08_reasoning_and_execution/iterative_reasoning/README.md) | `reasoning_and_execution.iterative_reasoning` | 15/10/2026 | Yes |
| [Mathematical Verification](../engineering_patterns/08_reasoning_and_execution/mathematical_verification/README.md) | `reasoning_and_execution.mathematical_verification` | 15/10/2026 | Yes |
| [Iterative independent verification](../engineering_patterns/08_reasoning_and_execution/plan_execute_verify/README.md) | `reasoning_and_execution.plan_execute_verify` | 11/10/2026 | Yes |
| [Reasoning Budget Control](../engineering_patterns/08_reasoning_and_execution/reasoning_budget_control/README.md) | `reasoning_and_execution.reasoning_budget_control` | 15/10/2026 | Yes |
| [Reflection And Critique](../engineering_patterns/08_reasoning_and_execution/reflection_and_critique/README.md) | `reasoning_and_execution.reflection_and_critique` | 15/10/2026 | Yes |
| [Sandboxed Python Execution](../engineering_patterns/08_reasoning_and_execution/sandboxed_python_execution/README.md) | `reasoning_and_execution.sandboxed_python_execution` | 15/10/2026 | Yes |
| [Self Correction](../engineering_patterns/08_reasoning_and_execution/self_correction/README.md) | `reasoning_and_execution.self_correction` | 15/10/2026 | Yes |
| [Stopping Conditions](../engineering_patterns/08_reasoning_and_execution/stopping_conditions/README.md) | `reasoning_and_execution.stopping_conditions` | 15/10/2026 | Yes |
| [Tool Augmented Reasoning](../engineering_patterns/08_reasoning_and_execution/tool_augmented_reasoning/README.md) | `reasoning_and_execution.tool_augmented_reasoning` | 15/10/2026 | Yes |

Run all offline patterns:

```bash
uv run --offline --locked python scripts/run_all_patterns.py
```

Only entries with a runnable manifest are listed; directories in the long-term roadmap are not claimed as implemented.
