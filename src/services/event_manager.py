"""Server-Sent Events manager for real-time updates."""
import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

logger = logging.getLogger(__name__)


class EventManager:
    """Manager for SSE connections and event broadcasting."""

    def __init__(self):
        """Initialize the event manager."""
        self._queues: list[asyncio.Queue] = []

    async def subscribe(self) -> AsyncGenerator[str, None]:
        """Subscribe to events and yield them as SSE format."""
        queue: asyncio.Queue = asyncio.Queue()
        self._queues.append(queue)

        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            self._queues.remove(queue)

    async def broadcast(self, data: dict[str, Any]) -> None:
        """Broadcast an event to all subscribers."""
        for queue in self._queues:
            try:
                await queue.put(data)
            except Exception as e:
                logger.error(f"Failed to broadcast to queue: {e}")

    @property
    def subscriber_count(self) -> int:
        """Get the number of active subscribers."""
        return len(self._queues)


# Global instance
event_manager = EventManager()
