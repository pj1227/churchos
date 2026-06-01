"""
routers/prayer_requests.py — Prayer board API endpoints.

Endpoint summary:
  POST   /prayer-requests            no auth   — submit a prayer request (rate-limited, AI-moderated)
  GET    /prayer-requests/public     no auth   — public board (approved only, email stripped)
  GET    /prayer-requests            member+   — full approved list (includes email for member context)
  GET    /prayer-requests/pending    staff+    — moderation queue (pending requests)
  PATCH  /prayer-requests/{id}       staff+    — approve or reject a request
  PATCH  /prayer-requests/{id}/answered staff+ — mark a request as answered

Security:
  - POST is unauthenticated but enforced by check_rate_limit (3/hr per IP).
  - AI moderation runs on every submission before storage.
  - GET /public is unauthenticated; email and moderation fields are stripped via PrayerRequestPublic schema.
  - GET (approved list) requires member role.
  - GET /pending and PATCH require staff role minimum.

Design note — why 201 regardless of AI decision:
  Even when AI rejects a submission, we return 201. The submitter experiences
  success, which preserves dignity and avoids giving bad actors information
  about our moderation thresholds. Rejected requests are stored in the DB
  with status='rejected' and are visible only to staff in the moderation queue.

How it connects:
  - app/main.py registers this router.
  - app/dependencies/rate_limit.py enforces IP rate limiting.
  - app/dependencies/ai_moderation.py moderates content.
  - app/dependencies/rbac.py enforces role requirements on protected routes.
  - app/crud/prayer_requests.py handles all Supabase calls.
  - app/schemas/prayer_request.py defines request/response shapes.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.config import settings
from app.crud import prayer_requests as prayer_crud
from app.crud import site_config as config_crud
from app.dependencies.ai_moderation import moderate_prayer_request
from app.dependencies.rate_limit import check_rate_limit
from app.dependencies.rbac import require_role
from app.schemas.prayer_request import (
    PrayerRequestCreate,
    PrayerRequestModerate,
    PrayerRequestPublic,
    PrayerRequestRead,
)
from app.services.email import send_prayer_notification

router = APIRouter(prefix="/prayer-requests", tags=["prayer"])


@router.post("", response_model=PrayerRequestRead, status_code=status.HTTP_201_CREATED)
async def submit_prayer_request(
    payload: PrayerRequestCreate,
    request: Request,
    _: None = Depends(check_rate_limit),
) -> dict:
    """
    Public endpoint — submit a prayer request.

    Rate-limited per IP (3/hr). AI moderates content before storage.
    Always returns 201 — submitter doesn't learn if their request was rejected.
    """
    moderation = moderate_prayer_request(payload.body)
    ai_approved = moderation["approved"]
    ai_reason   = moderation.get("reason")

    return prayer_crud.create_prayer_request(
        payload=payload,
        church_id=settings.church_id,
        ai_approved=ai_approved,
        ai_score=None,       # score not used in Phase 5; Gloo may return this in Phase 6
        ai_reason=ai_reason,
    )


@router.get("/public", response_model=list[PrayerRequestPublic])
async def list_public_prayer_requests() -> list[dict]:
    """
    Public board — approved, unanswered prayer requests. No auth required.

    Returns PrayerRequestPublic which intentionally omits email, ai_score,
    ai_reason, and moderated_by — no PII exposed to unauthenticated visitors.
    """
    return prayer_crud.list_prayer_requests(status="approved")


@router.get("/pending", response_model=list[PrayerRequestRead])
async def list_pending_prayer_requests(
    current_user: dict = Depends(require_role("staff")),
) -> list[dict]:
    """
    Moderation queue — all pending prayer requests. Staff+ required.
    Ordered newest-first so the most recent submissions appear at the top.
    """
    return prayer_crud.list_prayer_requests(status="pending")


@router.get("", response_model=list[PrayerRequestRead])
async def list_approved_prayer_requests(
    current_user: dict = Depends(require_role("member")),
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """
    Member-facing prayer list — approved requests only. Member+ required.
    Prayer requests are community content — not exposed publicly.
    """
    return prayer_crud.list_prayer_requests(status="approved")


@router.patch("/{prayer_id}", response_model=PrayerRequestRead)
async def moderate_prayer_request_endpoint(
    prayer_id: str,
    payload: PrayerRequestModerate,
    current_user: dict = Depends(require_role("staff")),
) -> dict:
    """
    Staff moderation action — approve or reject a prayer request.
    Records the moderator's user ID and timestamp.
    """
    existing = prayer_crud.get_prayer_request(prayer_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prayer request not found",
        )
    result = prayer_crud.moderate_prayer_request(
        prayer_id=prayer_id,
        payload=payload,
        moderator_id=current_user["id"],
    )

    # Send prayer chain email notification when approving
    if payload.status == "approved":
        prayer_chain_email = config_crud.get_raw_value("prayer_chain_email")
        if prayer_chain_email:
            send_prayer_notification(
                to=prayer_chain_email,
                prayer_body=existing.get("body", ""),
                submitter_name=existing.get("name"),
                is_anonymous=existing.get("is_anonymous", False),
            )

    return result


@router.patch("/{prayer_id}/answered", response_model=PrayerRequestRead)
async def mark_prayer_answered(
    prayer_id: str,
    current_user: dict = Depends(require_role("staff")),
) -> dict:
    """
    Mark a prayer request as answered. Staff+ required.
    Sets is_answered=True — the request remains visible in the active list
    but is visually distinguished and can be archived.
    """
    existing = prayer_crud.get_prayer_request(prayer_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prayer request not found",
        )
    return prayer_crud.set_answered(prayer_id, is_answered=True)
