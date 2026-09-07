"""API endpoints for exploring, summarizing, and downloading the Job Fraud Dataset."""

from typing import Optional
from fastapi import APIRouter, Query, Response, status
from app.services.dataset_service import dataset_service

router = APIRouter(prefix="/dataset", tags=["Dataset & Threat Corpus"])

@router.get(
    "/summary",
    status_code=status.HTTP_200_OK,
    summary="Get summary metrics and category distributions for the dataset",
)
def get_dataset_summary():
    return dataset_service.get_summary_stats()

@router.get(
    "/sample",
    status_code=status.HTTP_200_OK,
    summary="Search and preview dataset records",
)
def get_dataset_samples(
    q: Optional[str] = Query(None, description="Search query string"),
    category: Optional[str] = Query(None, description="Scam category filter"),
    is_scam: Optional[bool] = Query(None, description="Filter by scam status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return dataset_service.get_sample_records(
        query=q,
        category=category,
        is_scam=is_scam,
        limit=limit,
        offset=offset,
    )

@router.get(
    "/export/csv",
    status_code=status.HTTP_200_OK,
    summary="Download the complete Job Scam Dataset as CSV",
)
def download_dataset_csv():
    csv_data = dataset_service.export_csv_stream()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sentineljob_scam_intelligence_dataset.csv"},
    )
