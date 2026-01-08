from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from calf.message import Message


class Broker(ABC):
    """Abstract base class for message brokers."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the broker."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the broker."""
        ...

    @abstractmethod
    async def send(self, channel: str, message: Message) -> None:
        """Send a message to a channel."""
        ...

    @abstractmethod
    def subscribe(self, channel: str) -> AsyncIterator[Message]:
        """Subscribe to a channel and yield messages."""
        ...
