"""
Simple example workflow demonstrating Calf SDK usage.

Run locally:
    uv run examples/simple_workflow.py local

Run with Kafka:
    uv run examples/simple_workflow.py start --broker localhost:9092
"""

from calf import Calf, Message

calf = Calf()


@calf.on("documents.uploaded")
async def process_document(msg: Message) -> None:
    """Process uploaded documents."""
    print(f"Processing document: {msg.data}")

    # Simulate AI processing
    summary = f"Summary of document {msg.data.get('id', 'unknown')}"

    # Emit result to next stage
    await calf.emit(
        "documents.processed",
        {"id": msg.data.get("id"), "summary": summary},
        metadata=msg.metadata,
    )


@calf.on("documents.processed")
async def notify_completion(msg: Message) -> None:
    """Handle processed documents."""
    print(f"Document processed: {msg.data}")


if __name__ == "__main__":
    calf.run_app()
