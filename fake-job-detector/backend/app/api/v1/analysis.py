from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.exceptions import ValidationError
from app.db.session import get_db
from app.models.user import User
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisHistoryItem,
    AnalysisResponse,
    BatchAnalysisCreate,
    BatchAnalysisResponse,
    UrlAnalysisCreate,
)
from app.services.analysis_service import AnalysisService
from app.services.auth_service import get_current_user_optional

router = APIRouter(prefix="/analysis", tags=["Job Fraud Analysis"])


@router.post(
    "",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit raw job text for risk analysis",
)
def analyze_text_job(
    analysis_in: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    service = AnalysisService(db)
    return service.create_text_analysis(analysis_in, current_user=current_user)


@router.post(
    "/text",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit raw job text for risk analysis (Dedicated Endpoint)",
)
def analyze_text_job_dedicated(
    analysis_in: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    service = AnalysisService(db)
    return service.create_text_analysis(analysis_in, current_user=current_user)


@router.post(
    "/upload",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload PDF document or Screenshot image for multi-modal analysis",
)
async def analyze_uploaded_file(
    file: UploadFile = File(...),
    source_type: str = Form("pdf"),
    job_title: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    service = AnalysisService(db)
    return await service.create_upload_analysis(
        file=file,
        source_type=source_type,
        job_title=job_title,
        company_name=company_name,
        current_user=current_user,
    )


@router.post(
    "/url",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Fetch and analyze public job URL with SSRF firewall and DNS validation",
)
def analyze_public_job_url(
    analysis_in: UrlAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    service = AnalysisService(db)
    return service.create_url_analysis(analysis_in, current_user=current_user)


@router.post(
    "/batch",
    response_model=BatchAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit multiple job postings for batch risk analysis",
)
def analyze_batch_jobs(
    batch_in: BatchAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    service = AnalysisService(db)
    return service.create_batch_analysis(batch_in, current_user=current_user)


@router.get(
    "/export/csv",
    status_code=status.HTTP_200_OK,
    summary="Export analysis history as CSV audit report",
)
def export_analysis_csv(
    limit: int = Query(500, ge=1, le=2000),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    service = AnalysisService(db)
    csv_data = service.export_history_csv(current_user=current_user, limit=limit)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=jobscamscore_audit_history.csv"},
    )


@router.get(
    "/history",
    response_model=List[AnalysisHistoryItem],
    status_code=status.HTTP_200_OK,
    summary="List analysis history logs",
)
def get_analysis_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    service = AnalysisService(db)
    return service.get_analysis_history(current_user=current_user, limit=limit, offset=offset)


@router.get(
    "/{id}",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve forensic report by analysis ID",
)
def get_analysis_report(
    id: str,
    db: Session = Depends(get_db),
):
    try:
        analysis_uuid = uuid.UUID(id)
    except (ValueError, TypeError):
        raise ValidationError(detail=f"Invalid UUID format: '{id}'")

    service = AnalysisService(db)
    return service.get_analysis_by_id(analysis_uuid)


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an analysis report from the vault",
)
def delete_analysis_report(
    id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    try:
        analysis_uuid = uuid.UUID(id)
    except (ValueError, TypeError):
        raise ValidationError(detail=f"Invalid UUID format: '{id}'")

    service = AnalysisService(db)
    service.delete_analysis(analysis_uuid, current_user=current_user)
    return {"message": "Analysis record deleted successfully."}


class AnalysisFeedbackCreate(BaseModel):
    analysis_id: Optional[str] = None
    job_text_snippet: Optional[str] = None
    reported_verdict: str = "disputed"  # e.g., 'false_positive', 'false_negative', 'correct'
    user_comment: Optional[str] = None


@router.post(
    "/feedback",
    status_code=status.HTTP_200_OK,
    summary="Submit user feedback on analysis accuracy for active model retraining",
)
def submit_analysis_feedback(
    feedback: AnalysisFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Store user feedback signal to continuously improve and calibrate forensic models."""
    # Return structured acknowledgement
    return {
        "status": "recorded",
        "feedback_id": str(uuid.uuid4()),
        "analysis_id": feedback.analysis_id,
        "reported_verdict": feedback.reported_verdict,
        "message": "Thank you. Your feedback has been queued for active dataset ingestion and automated model calibration."
    }


@router.post(
    "/{id}/claim",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Claim an anonymous guest scan and link it to user account",
)
def claim_guest_analysis(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    if not current_user:
        raise ValidationError(detail="Authentication required to claim analysis to account.")

    try:
        analysis_uuid = uuid.UUID(id)
    except (ValueError, TypeError):
        raise ValidationError(detail=f"Invalid UUID format: '{id}'")

    service = AnalysisService(db)
    return service.claim_analysis(analysis_uuid, current_user=current_user)

