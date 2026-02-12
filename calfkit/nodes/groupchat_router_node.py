from abc import ABC
from typing import Annotated

from faststream import Context
from faststream.kafka.annotations import (
    KafkaBroker as BrokerAnnotation,
)

from calfkit.models.event_envelope import EventEnvelope
from calfkit.nodes.agent_router_node import AgentRouterNode
from calfkit.nodes.base_node import BaseNode, publish_to, subscribe_to


class GroupchatNode(BaseNode, ABC):
    """Node defining the llm chat node internal wiring.
    Separate from any logic for LLM persona or behaviour."""

    _on_enter_topic_name = "groupchat_prompted"
    _post_to_topic_name = "groupchat_generated"

    def __init__(
        self,
        agent_nodes: list[AgentRouterNode],
        *,
        shared_system_prompt_addition: str | None = None,
        **kwargs,
    ):
        self._agent_nodes = agent_nodes
        self._agent_node_topics = [
            node.subscribed_topic for node in agent_nodes if node.subscribed_topic is not None
        ]
        self._topic_to_agent_node = {
            node.subscribed_topic: node for node in agent_nodes if node.subscribed_topic is not None
        }
        self._shared_system_prompt_addition = shared_system_prompt_addition
        super().__init__(**kwargs)

    @subscribe_to(_on_enter_topic_name)
    @publish_to(_post_to_topic_name)
    async def _route_groupchat(
        self,
        event_envelope: EventEnvelope,
        correlation_id: Annotated[str, Context()],
        broker: BrokerAnnotation,
    ) -> EventEnvelope:
        if event_envelope.groupchat_data is None:  # manual None check for type checker
            raise RuntimeError("No groupchat data/config provided in groupchat node")

        if event_envelope.groupchat_data.groupchat_agent_topics is None:
            event_envelope.groupchat_data.groupchat_agent_topics = self._agent_node_topics

        if (
            event_envelope.groupchat_data.system_prompt_addition is None
            and self._shared_system_prompt_addition is not None
        ):
            # fallback system prompt
            event_envelope.groupchat_data.patch_system_prompt_addition(
                self._shared_system_prompt_addition
            )

        event_envelope.groupchat_data.commit_turn()

        original_event_envelope = event_envelope.model_copy(deep=True)

        event_envelope.pop_all_uncommited_agent_messages()
        flat_msgs = event_envelope.groupchat_data.flat_messages_from_turns_queue

        event_envelope.prepare_uncommitted_agent_messages(flat_msgs)
        event_envelope.groupchat_data.increment_turn_index()
        event_envelope.groupchat_data.increment_skip(
            reset=not event_envelope.groupchat_data.just_skipped
        )
        if event_envelope.groupchat_data.is_all_skipped():
            event_envelope.mark_as_end_of_turn()
            return event_envelope
        await self._call_agent(event_envelope, correlation_id=correlation_id, broker=broker)

        return original_event_envelope

    async def _call_agent(
        self, event_envelope: EventEnvelope, correlation_id: str, broker: BrokerAnnotation
    ):
        if event_envelope.groupchat_data is None:
            raise RuntimeError("Groupchat data is None for a call to a groupchat")
        if event_envelope.groupchat_data.groupchat_agent_topics is None:
            event_envelope.groupchat_data.groupchat_agent_topics = self._agent_node_topics

        agents_group_size = len(event_envelope.groupchat_data.groupchat_agent_topics)
        agent_input_topic = event_envelope.groupchat_data.groupchat_agent_topics[
            event_envelope.groupchat_data.turn_index % agents_group_size
        ]
        event_envelope.final_response_topic = self.subscribed_topic
        await broker.publish(
            event_envelope,
            topic=agent_input_topic,
            correlation_id=correlation_id,
        )
