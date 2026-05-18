from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.report_repository_port import IReportRepository
from app.domain.entities import TechnicalReport
from app.infrastructure.database.models import TechnicalReportModel


class ReportRepository(IReportRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, report: TechnicalReport) -> TechnicalReport:
        model = TechnicalReportModel(
            id=report.id,
            analysis_id=report.analysis_id,
            summary=report.summary,
            components=report.components,
            risks=report.risks,
            recommendations=report.recommendations,
            created_at=report.created_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_analysis_id(self, analysis_id: UUID) -> Optional[TechnicalReport]:
        result = await self._session.execute(
            select(TechnicalReportModel).where(
                TechnicalReportModel.analysis_id == analysis_id
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    @staticmethod
    def _to_entity(model: TechnicalReportModel) -> TechnicalReport:
        return TechnicalReport(
            id=model.id,
            analysis_id=model.analysis_id,
            summary=model.summary,
            components=model.components or [],
            risks=model.risks or [],
            recommendations=model.recommendations or [],
            created_at=model.created_at,
        )
