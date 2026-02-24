import asyncio
import logging
import os

from rich.live import Live

from calfkit.broker.broker import BrokerClient
from calfkit.runners.service import NodesService
from examples.auto_trading_bots.trading_tools import (
    execute_trade,
    get_portfolio,
    run_price_feed,
    store,
    view,
)

# Tools & Price Feed — Deploys trading tool workers and the Coinbase
# price feed.
#
# The price feed hydrates the shared price book that the trading
# tools read from when executing trades.
#
# Usage:
#     uv run python examples/auto_trading_bots/tools_and_dispatcher.py
#
# Prerequisites:
#     - Kafka broker running at localhost:9092

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )

    print("=" * 50)
    print("Tools & Price Feed Deployment")
    print("=" * 50)

    # Pre-create agent accounts so they appear immediately
    for agent_id in ("momentum", "brainrot-daytrader", "scalper"):
        store.get_or_create(agent_id)

    print(f"\nConnecting to Kafka broker at {KAFKA_BOOTSTRAP_SERVERS}...")
    broker = BrokerClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    service = NodesService(broker)

    # ── Tool nodes ───────────────────────────────────────────────
    print("\nRegistering trading tool nodes...")
    for tool in (execute_trade, get_portfolio):
        service.register_node(tool)
        print(f"  - {tool.tool_schema.name} (topic: {tool.subscribed_topic})")

    # ── Price feed ───────────────────────────────────────────────
    print("\nStarting Coinbase price feed...")
    price_feed_task = asyncio.create_task(run_price_feed())

    print("\nStarting portfolio dashboard...")

    with Live(view._build_layout(), auto_refresh=False, screen=True) as live:
        view.attach_live(live)
        try:
            await service.run()
        finally:
            price_feed_task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTools and price feed stopped.")
