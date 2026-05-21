from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities import TechnicalReport


class IReportRepository(ABC):
    @abstractmethod
    async def save(self, report: TechnicalReport) -> TechnicalReport:
        ...

    @abstractmethod
    async def get_by_analysis_id(self, analysis_id: UUID) -> Optional[TechnicalReport]:
        ...
