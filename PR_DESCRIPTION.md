# PR Description: SDK Refinements - Final Response Handling & Concurrent Execution

## Summary

This PR refines the SDK with several improvements including final response handling, tool call validation, concurrent execution support, and enhanced test utilities.

## Changes

### 1. Final Response Handling

**Files:** `calf/models/event_envelope.py`, `calf/nodes/agent_router_node.py`

- Added `final_response_topic` to `EventEnvelope` to specify where AI responses should be published
- Added `final_response` boolean flag to identify the final AI response to the user
- `_reply_to_sender()` now publishes to `event_envelope.final_response_topic` instead of the router's publish topic
- `invoke()` method now requires `final_response_topic` parameter

**Rationale:** Enables proper separation of intermediate messages (tracing) from final AI responses sent back to the user.

### 2. Tool Call Validation

**Files:** `calf/messages/util.py`, `calf/messages/__init__.py`

- Added `validate_tool_call_pairs()` utility function to verify all tool calls have corresponding results
- Validates messages in reverse order to check each `ToolCallPart` has a matching `ToolReturnPart` or `RetryPromptPart`
- Used in `AgentRouterNode` to determine when to call the model vs route tool calls

**Rationale:** Prevents routing errors by ensuring tool call-response pairs are properly matched before invoking the model.

### 3. Concurrent Execution Support

**File:** `calf/runners/node_runner.py`

- `register_on()` now accepts:
  - `max_workers`: Enable concurrent message processing
  - `group_id`: Consumer group ID for proper load balancing
  - `extra_publish_kwargs` / `extra_subscribe_kwargs`: Additional broker configuration
- Order changed to register subscriber before publisher (important for decorator chaining)

**Rationale:** Enables parallel tool execution by allowing multiple workers to process messages concurrently.

### 4. Bug Fix: Tool Topic Naming

**File:** `calf/nodes/base_tool_node.py`

- Fixed f-string formatting in topic names (was using literal `{func.__name__}` instead of interpolated values)

**Before:**
```python
@subscribe_to("tool_node.{func.__name__}.request")
@publish_to("tool_node.{func.__name__}.result")
```

**After:**
```python
@subscribe_to(f"tool_node.{func.__name__}.request")
@publish_to(f"tool_node.{func.__name__}.result")
```

### 5. Test Improvements

**Files:** `tests/test_agent_runner.py`, `tests/utils.py`

- Added `get_temperature` tool with 10s delay for testing concurrent execution
- Added `test_parallel_tool_calls` test to verify parallel tool execution
- Created `wait_for_condition()` utility for cleaner test condition waiting
- Separated `store` and `final_resp_store` for better test tracing
- Improved test output to show tool calls and response text
- Refactored queue iteration to use `queue.get_nowait()` with `queue.empty()` check

## Files Changed

| File | Changes |
|------|---------|
| `calf/messages/__init__.py` | Export new validation utility |
| `calf/messages/util.py` | Add `validate_tool_call_pairs()` |
| `calf/models/event_envelope.py` | Add `final_response_topic` and `final_response` fields |
| `calf/nodes/agent_router_node.py` | Use validation, fix response routing |
| `calf/nodes/base_tool_node.py` | Fix f-string bug |
| `calf/runners/node_runner.py` | Add concurrent execution support |
| `tests/test_agent_runner.py` | Add parallel test, improve test utilities |
| `tests/utils.py` | Add `wait_for_condition()` helper |

## Migration Guide

### Required: Update `invoke()` calls

The `invoke()` method now requires a `final_response_topic` parameter:

```python
# Before
await router_node.invoke(
    "What's the weather?",
    broker=broker,
)

# After
await router_node.invoke(
    "What's the weather?",
    broker=broker,
    final_response_topic="final_response",
)
```

### Optional: Enable concurrent execution

To enable parallel tool execution, specify `max_workers` when registering:

```python
tool_runner = ToolRunner(get_temperature)
tool_runner.register_on(broker, max_workers=2)  # 2 workers for parallel execution
```
