from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.community_scam import (
    CommunityScamFeedResponse,
    CommunityScamResponse,
    PublishScanToCommunityRequest,
)
from app.services.community_scam_service import community_scam_service

router = APIRouter(prefix="/community", tags=["Community Scam Intelligence"])


@router.get("/scams", response_model=CommunityScamFeedResponse)
def list_community_scams(
    query: Optional[str] = Query(None, description="Search keyword in title, company, domain, or snippet"),
    category: Optional[str] = Query(None, description="Filter by scam category (e.g. CHECK_FRAUD, TELEGRAM_INTERVIEW, CRYPTO_TASK)"),
    min_risk_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum risk score threshold"),
    verified_only: bool = Query(False, description="Filter only verified threat records"),
    sort_by: str = Query("newest", pattern="^(newest|highest_risk|most_confirmed)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Retrieve paginated community scam feed with real-time filtering and statistics."""
    feed = community_scam_service.get_scam_feed(
        db=db,
        query=query,
        category=category,
        min_risk_score=min_risk_score,
        verified_only=verified_only,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    return feed


@router.get("/scams/{scam_id}", response_model=CommunityScamResponse)
def get_community_scam_detail(
    scam_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve detailed threat dossier for a specific scam by UUID or public ID."""
    scam = community_scam_service.get_scam_by_id_or_public_id(db, scam_id)
    if not scam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Community scam threat '{scam_id}' was not found.",
        )
    return scam


@router.post("/scams/{scam_id}/confirm")
def confirm_community_threat(
    scam_id: str,
    db: Session = Depends(get_db),
):
    """Upvote / confirm a scam posting as a valid threat."""
    confirmations = community_scam_service.confirm_threat(db, scam_id)
    if confirmations is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Community scam threat '{scam_id}' was not found.",
        )
    return {
        "status": "success",
        "public_id": scam_id,
        "community_confirmations": confirmations,
        "message": "Thank you for confirming this threat and protecting fellow job seekers.",
    }


@router.post("/scams/publish", response_model=CommunityScamResponse, status_code=status.HTTP_201_CREATED)
def publish_scan_to_community(
    payload: PublishScanToCommunityRequest,
    db: Session = Depends(get_db),
):
    """Anonymize and publish a completed scan analysis to the public threat feed."""
    published = community_scam_service.publish_from_analysis(
        db=db,
        analysis_id=payload.analysis_id,
        custom_notes=payload.custom_notes,
    )
    if not published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to publish analysis to community feed. Ensure analysis ID is valid.",
        )
    return published


@router.get("/sync/status")
def get_threat_sync_status():
    """Retrieve the operational synchronization status of external federal and community threat feeds."""
    from app.services.threat_feed_sync_service import ThreatFeedSyncService
    return ThreatFeedSyncService.get_sync_status()


@router.post("/sync/refresh")
def trigger_threat_sync_refresh(
    db: Session = Depends(get_db),
):
    """Trigger an immediate synchronization cycle across federal watchlists and threat corpora."""
    from app.services.threat_feed_sync_service import ThreatFeedSyncService
    result = ThreatFeedSyncService.trigger_threat_feed_sync(db=db, force=True)
    return {
        "status": "success",
        "message": "Threat intelligence feeds synchronized successfully.",
        "details": result,
    }

