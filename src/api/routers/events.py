"""Server-Sent Events endpoint for real-time updates."""
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from src.services.event_manager import event_manager

router = APIRouter(tags=["events"])


@router.get("/events")
async def events():
    """SSE endpoint for real-time task status updates."""
    return EventSourceResponse(event_manager.subscribe())
