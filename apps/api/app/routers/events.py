"""
routers/events.py — Church event CRUD endpoints.

Endpoint summary:
  GET    /events          public   — paginated list, optional ?published_only=true
  GET    /events/{id}     public   — single event or 404
  POST   /events          staff+   — create a new event
  PATCH  /events/{id}     staff+   — partial update
  DELETE /events/{id}     admin+   — hard delete

How it connects:
  - app/main.py registers this router with prefix="/events"
  - app/crud/events.py handles all Supabase REST calls
  - app/dependencies/rbac.py enforces role requirements
  - app/schemas/event.py defines EventCreate, EventUpdate, EventRead
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.crud import events as event_crud
from app.dependencies.rbac import require_role
from app.schemas.event import EventCreate, EventRead, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventRead])
async def list_events(
    published_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Paginated event list. Public — no auth required."""
    return event_crud.list_events(
        published_only=published_only,
        limit=limit,
        offset=offset,
    )


@router.get("/{event_id}", response_model=EventRead)
async def get_event(event_id: str) -> dict:
    """Single event by ID. Public — no auth required."""
    event = event_crud.get_event(event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    current_user: dict = Depends(require_role("staff")),
) -> dict:
    """Create a new event. Staff+ required."""
    return event_crud.create_event(
        payload=payload,
        church_id=current_user.get("church_id") or settings.church_id,
        created_by=current_user["id"],
    )


@router.patch("/{event_id}", response_model=EventRead)
async def update_event(
    event_id: str,
    payload: EventUpdate,
    current_user: dict = Depends(require_role("staff")),
) -> dict:
    """Partially update an event. Staff+ required."""
    existing = event_crud.get_event(event_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event_crud.update_event(event_id, payload)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    current_user: dict = Depends(require_role("admin")),
) -> None:
    """Hard-delete an event. Admin+ required."""
    existing = event_crud.get_event(event_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    event_crud.delete_event(event_id)
