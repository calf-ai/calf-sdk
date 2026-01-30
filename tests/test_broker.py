import pytest
from faststream import FastStream
from faststream.kafka import KafkaBroker, TestKafkaBroker

broker = KafkaBroker("localhost:9092")
app = FastStream(broker)


@broker.subscriber("test-topic")
@broker.publisher("manual-reply-topic")
async def handle(
    name: str,
    user_id: int,
):
    print("Start handling")
    assert name == "John"
    assert user_id == 1
    print("Finished handling")
    return "Hello foo bar"


@broker.subscriber("test-reply-topic")
async def handle_reply(
    response: str,
):
    print("Start handling reply-topic")
    print(f"Response here: {response}")
    print("Finished handling reply-topic")


@broker.subscriber("manual-reply-topic")
async def manual_handle_reply(
    response: str,
):
    print("Start manual handling manual-reply-topic")
    print(f"Manual here: {response}")
    print("Finished manual handling manual-reply-topic")


@pytest.mark.asyncio
async def test_handle():
    print("\n\n===Start test===")
    async with TestKafkaBroker(broker) as br:
        await br.publish(
            {"name": "John", "user_id": 1}, topic="test-topic", reply_to="test-reply-topic"
        )
