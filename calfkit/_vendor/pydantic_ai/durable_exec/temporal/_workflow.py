from collections.abc import Sequence
from typing import Any

from ...durable_exec.temporal import TemporalAgent


class PydanticAIWorkflow:
    """Temporal Workflow base class that provides `__pydantic_ai_agents__` for direct agent registration."""

    __pydantic_ai_agents__: Sequence[TemporalAgent[Any, Any]]
