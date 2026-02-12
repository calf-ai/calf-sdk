from collections.abc import Sequence

from pydantic import Field

from calfkit._vendor.pydantic_ai import ModelMessage
from calfkit.models.bounded_queue import BoundedQueue
from calfkit.models.types import CompactBaseModel
from calfkit.nodes.agent_router_node import AgentRouterNode


class Turn(CompactBaseModel):
    messages: list[ModelMessage] = Field(default_factory=list)
    skipped: bool

    def add_new_message(self, message: ModelMessage):
        self.messages.append(message)

    def extend_new_messages(self, messages: list[ModelMessage]):
        self.messages.extend(messages)

    @classmethod
    def create_new_turn(cls, messages: list[ModelMessage] = [], skipped: bool = False) -> "Turn":
        return cls(messages=messages, skipped=skipped)


class GroupchatDataModel(CompactBaseModel):
    # Groupchat schema
    groupchat_agent_topics: list[str] | None
    _groupchat_turn_index: int = -1
    _consecutive_skips: int = 0
    system_prompt_addition: str | None = "\n\nYou are in a groupchat with other agents.\n\n"
    # Trailing list of the last N - 1 turns for a N-sized groupchat
    _turns_queue: BoundedQueue[Turn]
    _uncommitted_turn: Turn = Field(default_factory=Turn.create_new_turn)

    def increment_turn_index(self):
        self._groupchat_turn_index += 1

    def increment_skip(self, reset: bool = False):
        if reset:
            self._consecutive_skips = 0
        else:
            self._consecutive_skips += 1

    def patch_groupchat_agent_topics(self, agent_topics: list[str]):
        self.groupchat_agent_topics = agent_topics

    def patch_system_prompt_addition(self, system_prompt_addition: str):
        self.system_prompt_addition = system_prompt_addition

    def commit_turn(self):
        self._turns_queue.push(self._uncommitted_turn)
        self._uncommitted_turn = Turn.create_new_turn()

    def add_uncommitted_message_to_turn(self, message: ModelMessage):
        self._uncommitted_turn.add_new_message(message)

    def extend_uncommitted_messages_to_turn(self, messages: list[ModelMessage]):
        self._uncommitted_turn.extend_new_messages(messages)

    def is_all_skipped(self):
        return self._consecutive_skips >= len(self.groupchat_agent_topics or [])

    @property
    def just_skipped(self):
        if self._turns_queue:
            return self._turns_queue[-1].skipped
        return False

    @property
    def turn_index(self):
        return self._groupchat_turn_index

    @property
    def flat_messages_from_turns_queue(self) -> list[ModelMessage]:
        messages = []
        for turn in self._turns_queue.iter_items():
            messages.extend(turn.messages)
        return messages

    @classmethod
    def create_new_groupchat(
        cls,
        agent_nodes: Sequence[AgentRouterNode] | None = None,
        *,
        system_prompt_addition: str | None = None,
    ):
        agent_topics: list[str] = []
        agent_names: list[str] = []
        if agent_nodes is not None:
            for node in agent_nodes:
                if node.subscribed_topic is None:
                    continue
                agent_topics.append(node.subscribed_topic)
                agent_names.append(node.name or "general-agent (no name)")

        if system_prompt_addition is None:
            system_prompt_addition = (
                "\n\nYou are in a groupchat with other agents. The agents in the groupchat are:\n"
            )
            system_prompt_addition += "\n".join("- " + name for name in agent_names)
        return cls(
            groupchat_agent_topics=agent_topics if agent_nodes is not None else None,
            system_prompt_addition=system_prompt_addition,
            _turns_queue=BoundedQueue[Turn](maxlen=len(agent_topics) - 1),
        )
