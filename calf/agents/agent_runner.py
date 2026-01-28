from typing import Annotated, Awaitable, Callable

from faststream import Context
from pydantic_ai import ModelRequest, ModelResponse

from calf.broker.broker import Broker
from calf.models.event_envelope import EventEnvelope, ToolCallRequest
from calf.nodes.base_node import BaseNode, BaseToolNode
from calf.nodes.registrator import Registrator


class AgentRunner(Registrator):
    """Deployable unit orchestrating the internal routing to operate agents"""

    def __init__(
        self,
        chat_class: type[BaseNode],
        tool_classes: list[type[BaseToolNode]],
        handoff_classes: list[type[BaseNode]],
        reply_to_topic: str,
    ):
        self.chat = chat_class
        self.tools = tool_classes
        self.handoffs = handoff_classes
        self.reply_to_topic = reply_to_topic

        self.tools_topic_registry: dict[str, str] = {
            tool_class.tool_schema().name: tool_class.get_on_enter_topic()
            for tool_class in tool_classes
        }

        self.tool_response_topics = [tool.get_post_to_topic() for tool in self.tools]

        super().__init__()

    def register_on(
        self,
        broker: Broker,
        *,
        gather_func: Callable | Callable[..., Awaitable] | None = None,
    ):
        async def gather_response(
            ctx: EventEnvelope,
            correlation_id: Annotated[str, Context()],
        ):
            if ctx.latest_message is None:
                raise RuntimeError("The latest message is None")
            if isinstance(ctx.latest_message, ModelResponse):
                if ctx.latest_message.finish_reason == "tool_call" or ctx.latest_message.tool_calls:
                    print(f"Tool call here: {ctx.latest_message.tool_calls}")
                    print(f"Tool call thinking here: {ctx.latest_message.thinking}")
                    print(f"Tool call text here: {ctx.latest_message.text}")
                    for tool_call in ctx.latest_message.tool_calls:
                        await self._route_tool(tool_call, correlation_id, broker)
                else:
                    # reply to sender here
                    await self._reply_to_sender(ctx.latest_message, correlation_id, broker)
                    print(f"Response text here: {ctx.latest_message.text}")
            else:
                # tool call result block
                await self._call_model(ctx.latest_message, correlation_id, broker)

        if gather_func is None:
            gather_func = gather_response

        for topic in self.tool_response_topics:
            gather_func = broker.subscriber(topic)(gather_func)
        gather_func = broker.subscriber(self.chat.get_post_to_topic())(gather_func)

    async def _route_tool(
        self, generated_tool_call: ToolCallRequest, correlation_id: str, broker: Broker
    ) -> None:
        tool_topic = self.tools_topic_registry.get(generated_tool_call.tool_name)
        if tool_topic is None:
            # TODO: implement a short circuit to respond with an error message for when provided tool does not exist.
            return

        await broker.publish(
            EventEnvelope(
                kind="tool_call_request",
                trace_id=correlation_id,
                tool_call_request=generated_tool_call,
            ),
            topic=tool_topic,
            correlation_id=correlation_id,
        )

    async def _reply_to_sender(
        self, ai_response: ModelResponse, correlation_id: str, broker: Broker
    ) -> None:
        await broker.publish(
            EventEnvelope(
                kind="ai_response",
                trace_id=correlation_id,
                latest_message=ai_response,
            ),
            topic=self.reply_to_topic,
            correlation_id=correlation_id,
        )

    async def _call_model(
        self, tool_result: ModelRequest, correlation_id: str, broker: Broker
    ) -> None:
        await broker.publish(
            EventEnvelope(
                kind="tool_result",
                trace_id=correlation_id,
                latest_message=tool_result,
            ),
            topic=self.chat.get_on_enter_topic(),
            correlation_id=correlation_id,
        )
