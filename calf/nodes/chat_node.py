from abc import ABC
from typing import cast

from pydantic_ai import ModelResponse, ModelSettings
from pydantic_ai.direct import model_request
from pydantic_ai.models import Model, ModelRequestParameters

from calf.models.event_envelope import EventEnvelope
from calf.nodes.base_node import BaseNode


class ChatNode(BaseNode, ABC):
    """Entity for defining llm chat node internal wiring.
    Separate from any logic for LLM persona or behaviour."""

    # TODO: a separate layer of abstraction for LLM behaviour and persona. i.e. memory, prompting, etc.

    on_enter_topic = "ai_prompted"
    post_to_topic = "ai_generated"

    def __init__(
        self,
        model_client: Model,
        request_parameters: ModelRequestParameters | None = None,
        **kwargs,
    ):
        self.model_client = model_client
        self.request_parameters = request_parameters
        super().__init__(**kwargs)

    async def on_enter(self, event_envelope: EventEnvelope):
        latest_message = event_envelope.latest_message
        if latest_message is None:
            raise RuntimeError("latest message must not be None")
        request_parameters = event_envelope.patch_model_request_params or self.request_parameters
        patch_model_settings = event_envelope.patch_model_settings
        model_response: ModelResponse = await model_request(
            model=self.model_client,
            messages=[latest_message],
            model_settings=cast(ModelSettings | None, patch_model_settings),
            model_request_parameters=request_parameters,
        )
        return_envelope = event_envelope.model_copy()
        return_envelope.kind = "ai_response"
        update_values = EventEnvelope(
            kind="ai_response",
            latest_message=model_response,
        )
        return_envelope = event_envelope.model_copy(
            update=update_values.model_dump(exclude_unset=True)
        )
        return return_envelope

    @classmethod
    def get_on_enter_topic(cls) -> str:
        return cls.on_enter_topic

    @classmethod
    def get_post_to_topic(cls) -> str:
        return cls.post_to_topic
