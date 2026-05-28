"""
routers/sermons.py — Sermon CRUD endpoints.

Endpoint summary:
  GET    /sermons          public   — paginated list, optional ?published_only=true
  GET    /sermons/{id}     public   — single sermon or 404
  POST   /sermons          staff+   — manual sermon creation (non-Logos churches)
  PATCH  /sermons/{id}     staff+   — partial update of human-editable fields
  DELETE /sermons/{id}     admin+   — hard delete

Note on PATCH vs PUT:
  PUT (full replace) is inappropriate here because many columns are managed by
  the Logos sync process and should never be overwritten by an admin form.
  PATCH lets the admin send only the fields they intend to change.

How it connects:
  - app/main.py registers this router with prefix="/sermons"
  - app/crud/sermons.py handles all Supabase REST calls
  - app/dependencies/rbac.py enforces role requirements
  - app/schemas/sermon.py defines SermonCreate, SermonUpdate, SermonRead
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.crud import sermons as sermon_crud
from app.dependencies.rbac import require_role
from app.schemas.sermon import SermonCreate, SermonRead, SermonUpdate

router = APIRouter(prefix="/sermons", tags=["sermons"])


@router.get("", response_model=list[SermonRead])
async def list_sermons(
    published_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Paginated sermon list. Public — no auth required."""
    return sermon_crud.list_sermons(
        published_only=published_only,
        limit=limit,
        offset=offset,
    )


@router.get("/{sermon_id}", response_model=SermonRead)
async def get_sermon(sermon_id: str) -> dict:
    """Single sermon by ID. Public — no auth required."""
    sermon = sermon_crud.get_sermon(sermon_id)
    if sermon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sermon not found")
    return sermon


@router.post("", response_model=SermonRead, status_code=status.HTTP_201_CREATED)
async def create_sermon(
    payload: SermonCreate,
    current_user: dict = Depends(require_role("staff")),
) -> dict:
    """
    Manually create a sermon. Staff+ required.
    Intended for churches not using Logos sync.
    """
    return sermon_crud.create_sermon(
        payload=payload,
        church_id=current_user.get("church_id") or settings.church_id,
    )


@router.patch("/{sermon_id}", response_model=SermonRead)
async def update_sermon(
    sermon_id: str,
    payload: SermonUpdate,
    current_user: dict = Depends(require_role("staff")),
) -> dict:
    """
    Partially update a sermon's human-editable fields. Staff+ required.
    Logos sync fields (logos_id, logos_url, etc.) are ignored even if sent.
    """
    existing = sermon_crud.get_sermon(sermon_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sermon not found")
    return sermon_crud.update_sermon(sermon_id, payload)


@router.delete("/{sermon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sermon(
    sermon_id: str,
    current_user: dict = Depends(require_role("admin")),
) -> None:
    """Hard-delete a sermon. Admin+ required."""
    existing = sermon_crud.get_sermon(sermon_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sermon not found")
    sermon_crud.delete_sermon(sermon_id)
