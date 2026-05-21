import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.application.use_cases.create_report import CreateReportUseCase

pytestmark = pytest.mark.asyncio

_COMPONENTS = ["api gateway", "backend", "database"]
_RISKS = ["Ausência de load balancer."]
_RECS = ["Adicionar autenticação entre serviços."]
_SUMMARY = "Foram identificados 3 componentes."


async def test_create_report_success(mock_repo, mock_report, analysis_id):
    mock_repo.get_by_analysis_id = AsyncMock(return_value=None)
    mock_repo.save = AsyncMock(return_value=mock_report)

    use_case = CreateReportUseCase(mock_repo)
    result = await use_case.execute(analysis_id, _SUMMARY, _COMPONENTS, _RISKS, _RECS)

    mock_repo.save.assert_called_once()
    assert result.summary == mock_report.summary
    assert result.components == mock_report.components


async def test_create_report_idempotent_returns_existing(mock_repo, mock_report, analysis_id):
    """Second call with same analysis_id returns existing report without saving again."""
    mock_repo.get_by_analysis_id = AsyncMock(return_value=mock_report)

    use_case = CreateReportUseCase(mock_repo)
    result = await use_case.execute(analysis_id, _SUMMARY, _COMPONENTS, _RISKS, _RECS)

    mock_repo.save.assert_not_called()
    assert result is mock_report


async def test_create_report_invalid_analysis_id(mock_repo):
    use_case = CreateReportUseCase(mock_repo)

    with pytest.raises(ValueError, match="Invalid analysis_id"):
        await use_case.execute("not-a-uuid", _SUMMARY, _COMPONENTS, _RISKS, _RECS)
    mock_repo.save.assert_not_called()


async def test_create_report_empty_lists(mock_repo, mock_report, analysis_id):
    """Empty components/risks/recommendations must be accepted."""
    mock_repo.get_by_analysis_id = AsyncMock(return_value=None)
    from dataclasses import replace
    empty_report = replace(mock_report, components=[], risks=[], recommendations=[])
    mock_repo.save = AsyncMock(return_value=empty_report)

    use_case = CreateReportUseCase(mock_repo)
    result = await use_case.execute(analysis_id, "No components.", [], [], [])

    assert result.components == []
    assert result.risks == []
    assert result.recommendations == []


async def test_create_report_persists_correct_data(mock_repo, mock_report, analysis_id):
    """Verify the data passed to save matches the input."""
    mock_repo.get_by_analysis_id = AsyncMock(return_value=None)
    mock_repo.save = AsyncMock(return_value=mock_report)

    use_case = CreateReportUseCase(mock_repo)
    await use_case.execute(analysis_id, _SUMMARY, _COMPONENTS, _RISKS, _RECS)

    saved_report = mock_repo.save.call_args[0][0]
    assert str(saved_report.analysis_id) == analysis_id
    assert saved_report.summary == _SUMMARY
    assert saved_report.components == _COMPONENTS
    assert saved_report.risks == _RISKS
    assert saved_report.recommendations == _RECS
