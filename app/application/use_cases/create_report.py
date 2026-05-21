import logging
import uuid
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from app.application.ports.report_repository_port import IReportRepository
from app.domain.entities import TechnicalReport

logger = logging.getLogger(__name__)


class CreateReportUseCase:
    def __init__(self, repository: IReportRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        analysis_id: str,
        summary: str,
        components: List[str],
        risks: List[str],
        recommendations: List[str],
    ) -> TechnicalReport:
        try:
            uid = UUID(analysis_id)
        except ValueError as exc:
            raise ValueError(f"Invalid analysis_id: {analysis_id}") from exc

        # Idempotency: return existing report if one already exists
        existing = await self._repository.get_by_analysis_id(uid)
        if existing:
            logger.info(
                "Report already exists, returning existing",
                extra={"event": "report_exists", "analysis_id": analysis_id},
            )
            return existing

        report = TechnicalReport(
            id=uuid.uuid4(),
            analysis_id=uid,
            summary=summary,
            components=components,
            risks=risks,
            recommendations=recommendations,
            created_at=datetime.now(timezone.utc),
        )
        saved = await self._repository.save(report)
        logger.info(
            "Report generated and persisted",
            extra={"event": "report_generated", "analysis_id": analysis_id},
        )
        return saved
