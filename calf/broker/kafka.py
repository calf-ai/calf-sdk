from collections.abc import AsyncIterator

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer  # type: ignore[import-untyped]

from calf.broker.base import Broker
from calf.message import Message


class KafkaBroker(Broker):
    """Kafka broker for production use."""

    def __init__(self, bootstrap_servers: str) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None
        self._consumers: list[AIOKafkaConsumer] = []

    async def connect(self) -> None:
        """Establish connection to Kafka."""
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            value_serializer=lambda m: m.model_dump_json().encode("utf-8"),
        )
        await self._producer.start()

    async def disconnect(self) -> None:
        """Close connection to Kafka."""
        if self._producer:
            await self._producer.stop()
            self._producer = None

        for consumer in self._consumers:
            await consumer.stop()
        self._consumers.clear()

    async def send(self, channel: str, message: Message) -> None:
        """Send a message to a Kafka topic."""
        if not self._producer:
            raise RuntimeError("Broker is not connected")

        await self._producer.send_and_wait(channel, message)

    async def subscribe(self, channel: str) -> AsyncIterator[Message]:
        """Subscribe to a Kafka topic and yield messages."""
        consumer = AIOKafkaConsumer(
            channel,
            bootstrap_servers=self._bootstrap_servers,
            value_deserializer=lambda m: Message.model_validate_json(m),
            auto_offset_reset="earliest",
        )
        self._consumers.append(consumer)
        await consumer.start()

        try:
            async for record in consumer:
                yield record.value
        finally:
            await consumer.stop()
            self._consumers.remove(consumer)
