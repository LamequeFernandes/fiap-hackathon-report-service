import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.application.use_cases.get_report import GetReportUseCase
from app.domain.exceptions import ReportNotFoundError

pytestmark = pytest.mark.asyncio


async def test_get_report_success(mock_repo, mock_report, analysis_id):
    mock_repo.get_by_analysis_id = AsyncMock(return_value=mock_report)

    use_case = GetReportUseCase(mock_repo)
    result = await use_case.execute(str(mock_report.analysis_id))

    assert result is mock_report
    mock_repo.get_by_analysis_id.assert_called_once()


async def test_get_report_not_found(mock_repo):
    mock_repo.get_by_analysis_id = AsyncMock(return_value=None)

    use_case = GetReportUseCase(mock_repo)

    with pytest.raises(ReportNotFoundError) as exc_info:
        await use_case.execute(str(uuid4()))

    assert "not found" in str(exc_info.value)


async def test_get_report_invalid_uuid(mock_repo):
    use_case = GetReportUseCase(mock_repo)

    with pytest.raises(ReportNotFoundError):
        await use_case.execute("not-a-valid-uuid")
    mock_repo.get_by_analysis_id.assert_not_called()


async def test_get_report_returns_all_fields(mock_repo, mock_report):
    mock_repo.get_by_analysis_id = AsyncMock(return_value=mock_report)

    use_case = GetReportUseCase(mock_repo)
    result = await use_case.execute(str(mock_report.analysis_id))

    assert result.summary == mock_report.summary
    assert result.components == mock_report.components
    assert result.risks == mock_report.risks
    assert result.recommendations == mock_report.recommendations
    assert result.created_at == mock_report.created_at
