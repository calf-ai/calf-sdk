from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

from calf.broker.base import Broker
from calf.message import Message


class Calf:
    """Main client for building event-driven AI workflows."""

    def __init__(self) -> None:
        self._broker: Broker | None = None
        self._handlers: dict[str, Callable[[Message], Awaitable[None]]] = {}
        self._listener_tasks: list[asyncio.Task[None]] = []

    def _set_broker(self, broker: Broker) -> None:
        """Set the broker instance (called by CLI)."""
        self._broker = broker

    async def emit(
        self,
        channel: str,
        data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Send a message to a channel."""
        if not self._broker:
            raise RuntimeError("Broker is not configured. Use run_app() to start.")

        message = Message(
            data=data,
            channel=channel,
            metadata=metadata or {},
        )
        await self._broker.send(channel, message)

    async def listen(self, channel: str) -> AsyncIterator[Message]:
        """Receive messages from a channel as an async iterator."""
        if not self._broker:
            raise RuntimeError("Broker is not configured. Use run_app() to start.")

        async for message in self._broker.subscribe(channel):
            yield message

    def on(
        self, channel: str
    ) -> Callable[[Callable[[Message], Awaitable[None]]], Callable[[Message], Awaitable[None]]]:
        """Decorator to register a handler for a channel."""

        def decorator(
            fn: Callable[[Message], Awaitable[None]],
        ) -> Callable[[Message], Awaitable[None]]:
            self._handlers[channel] = fn
            return fn

        return decorator

    async def _start(self) -> None:
        """Start the broker and all registered handlers."""
        if not self._broker:
            raise RuntimeError("Broker is not configured. Use run_app() to start.")

        await self._broker.connect()

        for channel, handler in self._handlers.items():
            task = asyncio.create_task(self._run_handler(channel, handler))
            self._listener_tasks.append(task)

    async def _run_handler(
        self,
        channel: str,
        handler: Callable[[Message], Awaitable[None]],
    ) -> None:
        """Run a handler for messages on a channel."""
        if not self._broker:
            return

        async for message in self._broker.subscribe(channel):
            try:
                await handler(message)
            except Exception as e:
                # Propagate to user - they handle errors
                raise e

    async def _stop(self) -> None:
        """Stop all handlers and disconnect from broker."""
        for task in self._listener_tasks:
            task.cancel()

        if self._listener_tasks:
            await asyncio.gather(*self._listener_tasks, return_exceptions=True)

        self._listener_tasks.clear()

        if self._broker:
            await self._broker.disconnect()

    def run_app(self) -> None:
        """Start the workflow with CLI argument parsing."""
        from calf.cli import run_app

        run_app(self)
