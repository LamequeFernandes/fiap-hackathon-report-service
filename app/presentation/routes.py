import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.create_report import CreateReportUseCase
from app.application.use_cases.get_report import GetReportUseCase
from app.domain.exceptions import ReportNotFoundError
from app.infrastructure.database.repositories import ReportRepository
from app.infrastructure.database.session import get_session
from app.presentation.schemas import (
    CreateReportRequest,
    HealthResponse,
    ReportResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse(status="healthy", service="report-service")


@router.post("/reports", status_code=201, response_model=ReportResponse, tags=["reports"])
async def create_report(
    body: CreateReportRequest,
    session: AsyncSession = Depends(get_session),
) -> ReportResponse:
    error_id = str(uuid.uuid4())
    try:
        use_case = CreateReportUseCase(ReportRepository(session))
        report = await use_case.execute(
            analysis_id=body.analysis_id,
            summary=body.summary,
            components=body.components,
            risks=body.risks,
            recommendations=body.recommendations,
        )
        return ReportResponse(
            analysis_id=str(report.analysis_id),
            summary=report.summary,
            components=report.components,
            risks=report.risks,
            recommendations=report.recommendations,
            created_at=report.created_at,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        logger.exception("Unexpected error creating report", extra={"error_id": error_id})
        raise HTTPException(
            status_code=500, detail=f"Internal server error. Reference: {error_id}"
        )


@router.get("/reports/{analysis_id}", response_model=ReportResponse, tags=["reports"])
async def get_report(
    analysis_id: str,
    session: AsyncSession = Depends(get_session),
) -> ReportResponse:
    error_id = str(uuid.uuid4())
    try:
        use_case = GetReportUseCase(ReportRepository(session))
        report = await use_case.execute(analysis_id)
        return ReportResponse(
            analysis_id=str(report.analysis_id),
            summary=report.summary,
            components=report.components,
            risks=report.risks,
            recommendations=report.recommendations,
            created_at=report.created_at,
        )
    except ReportNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Report for analysis {analysis_id} not found."
        )
    except Exception:
        logger.exception("Unexpected error getting report", extra={"error_id": error_id})
        raise HTTPException(
            status_code=500, detail=f"Internal server error. Reference: {error_id}"
        )
