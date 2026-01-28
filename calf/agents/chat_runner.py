from httpx import Timeout
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIChatModelSettings
from pydantic_ai.providers.openai import OpenAIProvider

from calf.agents.node_runner import BaseNodeRunner
from calf.broker.broker import Broker
from calf.nodes.chat_node import ChatNode
from calf.providers.pydantic_ai.openai import OpenAIModelClient


class ChatRunner(BaseNodeRunner):
    """Entity for server/worker-side ops. Mainly used for server-side deployment.
    Pass in a client"""

    def __init__(self, model_client: Model, **kwargs):
        self.model_client = model_client
        self.node = ChatNode(
            model_client,
        )
        super().__init__(self.node, **kwargs)
