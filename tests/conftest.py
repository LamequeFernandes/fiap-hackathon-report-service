import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

from app.domain.entities import TechnicalReport


@pytest.fixture
def analysis_id():
    return str(uuid4())


@pytest.fixture
def mock_report(analysis_id):
    return TechnicalReport(
        id=uuid4(),
        analysis_id=uuid4(),
        summary="Foram identificados 3 componentes arquiteturais.",
        components=["api gateway", "backend", "database"],
        risks=["Ausência de load balancer."],
        recommendations=["Adicionar autenticação entre serviços."],
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_repo(mock_report):
    repo = AsyncMock()
    repo.save = AsyncMock(return_value=mock_report)
    repo.get_by_analysis_id = AsyncMock(return_value=None)
    return repo
