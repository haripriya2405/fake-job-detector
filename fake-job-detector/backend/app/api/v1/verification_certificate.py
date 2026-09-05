from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.certificate import VerificationCertificateResponse
from app.services.certificate_service import certificate_service

router = APIRouter(prefix="/verify", tags=["Public Verification Certificates & Badges"])


@router.get("/{identifier}", response_model=VerificationCertificateResponse)
def get_verification_certificate(
    identifier: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Retrieve public cryptographic verification certificate for a job analysis."""
    base_url = str(request.base_url).rstrip("/")
    cert = certificate_service.get_certificate_data(db=db, identifier=identifier, base_url=base_url)
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification certificate '{identifier}' was not found or has expired.",
        )
    return cert


@router.get("/{identifier}/badge.svg")
def get_verification_badge_svg(
    identifier: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Render and stream live SVG verification badge for embed in websites, LinkedIn, or GitHub."""
    base_url = str(request.base_url).rstrip("/")
    cert = certificate_service.get_certificate_data(db=db, identifier=identifier, base_url=base_url)
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification certificate '{identifier}' was not found.",
        )

    svg_content = certificate_service.render_svg_badge(cert)
    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "public, max-age=3600, s-maxage=3600",
            "Content-Disposition": f'inline; filename="jobscamscore-badge-{cert.certificate_id}.svg"',
        },
    )
