# Author: Vishal Bulbule
# Date: 2026-09-22

"""Streaming tool: an async generator the agent reacts to while it runs.

watch_stock is an async function typed to return AsyncGenerator. ADK runs it
as a background task in a live session: the model immediately gets a
"pending" response, and every yielded value is then sent to the model as a
further function response, so it can comment on each tick without being
asked again.

Streaming tools only run under runner.run_live(), which in adk web means a
voice session started with the call (phone) button. stop_streaming is ADK's reserved tool name for cancelling
a running stream; ADK intercepts the call by name, so the function body is
never used.
"""

import asyncio
import os
import random
from typing import AsyncGenerator

from google.adk.agents import LlmAgent

LIVE_MODEL = os.getenv("LIVE_MODEL", "gemini-live-2.5-flash-native-audio")
TICKS = 5
TICK_INTERVAL_S = 2.0


async def watch_stock(symbol: str) -> AsyncGenerator[dict, None]:
    """Streams price updates for a stock symbol. Call once; it keeps sending updates.

    Prices are a random walk in this sample. A real tool would read a market
    data feed and yield whenever the price changes.

    Args:
        symbol: Ticker symbol to watch, for example "TSLA".

    Yields:
        A dict with status, symbol, price, and tick number.
    """
    price = 100.0
    for tick in range(TICKS):
        price += random.uniform(-5.0, 5.0)
        update = {
            "status": "success",
            "symbol": symbol,
            "price": round(price, 2),
            "tick": tick,
        }
        # The updates go from ADK straight to the model, not to the client, so
        # the adk web terminal is the only place they are visible.
        print(f"[tool-yield] {update}")
        yield update
        await asyncio.sleep(TICK_INTERVAL_S)


def stop_streaming(function_name: str) -> None:
    """Stops a running streaming tool.

    Args:
        function_name: Name of the streaming tool to stop, for example "watch_stock".
    """


root_agent = LlmAgent(
    name="stock_watcher",
    model=LIVE_MODEL,
    instruction=(
        "You watch stocks for the user. When the user names a symbol, call "
        "watch_stock once and react to each update in one short sentence: "
        "spikes, dips, or crossing a round number. Never call watch_stock "
        "again to poll. If the user asks you to stop, call stop_streaming "
        "with function_name 'watch_stock'."
    ),
    tools=[watch_stock, stop_streaming],
)
