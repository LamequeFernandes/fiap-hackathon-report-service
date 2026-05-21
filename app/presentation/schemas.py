from datetime import datetime
from typing import List

from pydantic import BaseModel


class CreateReportRequest(BaseModel):
    analysis_id: str
    summary: str
    components: List[str]
    risks: List[str]
    recommendations: List[str]


class ReportResponse(BaseModel):
    analysis_id: str
    summary: str
    components: List[str]
    risks: List[str]
    recommendations: List[str]
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    service: str
