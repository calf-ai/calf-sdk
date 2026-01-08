from __future__ import annotations

import asyncio
import signal
from typing import TYPE_CHECKING

import typer

if TYPE_CHECKING:
    from calf.client import Calf

app = typer.Typer(
    name="calf",
    help="Event-driven SDK for building AI workflows",
    add_completion=False,
)


def _run_with_signal_handling(calf: Calf) -> None:
    """Run the Calf client with graceful shutdown on SIGINT/SIGTERM."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    shutdown_event = asyncio.Event()

    def signal_handler() -> None:
        shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    async def run() -> None:
        await calf._start()
        await shutdown_event.wait()
        await calf._stop()

    try:
        loop.run_until_complete(run())
    finally:
        loop.close()


@app.command()
def local(ctx: typer.Context) -> None:
    """Run workflow with in-memory broker for local development."""
    from calf.broker.memory import MemoryBroker

    calf: Calf = ctx.obj
    calf._set_broker(MemoryBroker())
    typer.echo("Starting Calf with in-memory broker...")
    _run_with_signal_handling(calf)


@app.command()
def start(
    ctx: typer.Context,
    broker: str = typer.Option(..., "--broker", "-b", help="Kafka broker URL"),
) -> None:
    """Run workflow with Kafka broker for production."""
    from calf.broker.kafka import KafkaBroker

    calf: Calf = ctx.obj
    calf._set_broker(KafkaBroker(broker))
    typer.echo(f"Starting Calf with Kafka broker at {broker}...")
    _run_with_signal_handling(calf)


def run_app(calf: Calf) -> None:
    """Entry point for running a Calf workflow from command line."""
    app(obj=calf)
