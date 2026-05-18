from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID


@dataclass
class TechnicalReport:
    id: UUID
    analysis_id: UUID
    summary: str
    components: List[str]
    risks: List[str]
    recommendations: List[str]
    created_at: datetime
