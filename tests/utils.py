import asyncio
import time
from collections.abc import Callable


async def wait_for_condition(
    predicate: Callable[[], bool],
    timeout: float = 20.0,
    poll_interval: float = 0.1,
) -> None:
    """Wait for a predicate to become True.

    Args:
        predicate: A callable that returns True when the condition is met.
        timeout: Maximum time to wait in seconds.
        poll_interval: Time between checks in seconds.

    Raises:
        asyncio.TimeoutError: If the condition is not met within the timeout.

    Example:
        await wait_for_condition(lambda: trace_id in store, timeout=10.0)
    """
    start = time.monotonic()
    print(f"[wait_for_condition] start={start:.2f}, timeout={timeout}")
    while not predicate():
        elapsed = time.monotonic() - start
        if elapsed > timeout:
            print(f"[wait_for_condition] TIMEOUT! elapsed={elapsed:.2f}")
            raise asyncio.TimeoutError(f"Condition not met within {timeout}s timeout")
        await asyncio.sleep(poll_interval)
    print(f"[wait_for_condition] done, elapsed={time.monotonic() - start:.2f}")
