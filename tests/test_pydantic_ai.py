from pydantic_ai.models.openai import Model, OpenAIChatModel
from pydantic_ai import Agent
from calf.providers.base import ProviderClient
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    RunContext,
    cli,
    function_tool,
    inference,
)


class TestPydantic(ProviderClient):
    def __init__(self):
        self.model = OpenAIChatModel()
    async def generate(self):
        
        
