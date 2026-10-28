# LangGraph patterns

Use LangGraph for explicit state and branch control. Keep external side effects
outside the graph until the workflow reaches its review or approval node.

| Pattern | Suitable task |
| --- | --- |
| `specialist_routing` | Direct an intake message to a bounded specialist queue. |
| `human_approval_gate` | Hold a draft until a reviewer decides approve or revise. |
| `recovery_loop` | Retry validation with a strict attempt limit, then escalate. |
| `long_running_case` | Track an intake-to-follow-up workflow through named states. |

