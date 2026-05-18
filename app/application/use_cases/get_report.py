import logging
from uuid import UUID

from app.application.ports.report_repository_port import IReportRepository
from app.domain.entities import TechnicalReport
from app.domain.exceptions import ReportNotFoundError

logger = logging.getLogger(__name__)


class GetReportUseCase:
    def __init__(self, repository: IReportRepository) -> None:
        self._repository = repository

    async def execute(self, analysis_id: str) -> TechnicalReport:
        try:
            uid = UUID(analysis_id)
        except ValueError:
            raise ReportNotFoundError(analysis_id)

        report = await self._repository.get_by_analysis_id(uid)
        if report is None:
            raise ReportNotFoundError(analysis_id)
        return report
