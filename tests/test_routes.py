import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from uuid import uuid4

from httpx import ASGITransport, AsyncClient

from app.domain.exceptions import ReportNotFoundError
from app.infrastructure.database.session import get_session
from app.main import app
from app.presentation.routes import _verify_internal_auth

pytestmark = pytest.mark.asyncio

_ANALYSIS_ID = str(uuid4())
_NOW = datetime.now(timezone.utc).isoformat()

_REPORT_PAYLOAD = {
    "analysis_id": _ANALYSIS_ID,
    "summary": "Foram identificados 4 componentes arquiteturais.",
    "components": ["api gateway", "backend", "database", "redis"],
    "risks": ["Ausência de load balancer.", "Ausência de autenticação explícita."],
    "recommendations": [
        "Adicionar autenticação entre serviços.",
        "Implementar circuit breaker.",
    ],
}

_REPORT_RESPONSE = {**_REPORT_PAYLOAD, "created_at": _NOW}


# Fixture: HTTP client with mocked DB session

@pytest.fixture
async def client():
    async def _override_session():
        yield AsyncMock()

    app.dependency_overrides[get_session] = _override_session
    # Internal auth is tested separately; bypass it for business-logic focused tests.
    app.dependency_overrides[_verify_internal_auth] = lambda: None
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# Health

async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "report-service"


# POST /reports

async def test_create_report_success(client, mock_report):
    with patch("app.presentation.routes.ReportRepository"), \
         patch("app.presentation.routes.CreateReportUseCase") as MockUC:
        MockUC.return_value.execute = AsyncMock(return_value=mock_report)

        response = await client.post("/reports", json=_REPORT_PAYLOAD)

    assert response.status_code == 201
    data = response.json()
    assert "analysis_id" in data
    assert "summary" in data
    assert "components" in data
    assert "risks" in data
    assert "recommendations" in data
    assert "created_at" in data


async def test_create_report_invalid_analysis_id(client):
    with patch("app.presentation.routes.ReportRepository"), \
         patch("app.presentation.routes.CreateReportUseCase") as MockUC:
        MockUC.return_value.execute = AsyncMock(
            side_effect=ValueError("Invalid analysis_id: bad-id")
        )
        payload = {**_REPORT_PAYLOAD, "analysis_id": "bad-id"}
        response = await client.post("/reports", json=payload)

    assert response.status_code == 422


async def test_create_report_missing_required_field(client):
    """Pydantic validation rejects request missing required fields."""
    incomplete = {"analysis_id": _ANALYSIS_ID, "summary": "Missing components/risks/recs"}
    response = await client.post("/reports", json=incomplete)
    assert response.status_code == 422


async def test_create_report_idempotent(client, mock_report):
    """Calling POST /reports twice for the same analysis_id returns the existing report."""
    with patch("app.presentation.routes.ReportRepository"), \
         patch("app.presentation.routes.CreateReportUseCase") as MockUC:
        MockUC.return_value.execute = AsyncMock(return_value=mock_report)

        r1 = await client.post("/reports", json=_REPORT_PAYLOAD)
        r2 = await client.post("/reports", json=_REPORT_PAYLOAD)

    assert r1.status_code == 201
    assert r2.status_code == 201


# GET /reports/{analysis_id}

async def test_get_report_success(client, mock_report):
    with patch("app.presentation.routes.ReportRepository"), \
         patch("app.presentation.routes.GetReportUseCase") as MockUC:
        MockUC.return_value.execute = AsyncMock(return_value=mock_report)

        response = await client.get(f"/reports/{_ANALYSIS_ID}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["components"], list)
    assert isinstance(data["risks"], list)
    assert isinstance(data["recommendations"], list)
    assert "summary" in data


async def test_get_report_not_found(client):
    with patch("app.presentation.routes.ReportRepository"), \
         patch("app.presentation.routes.GetReportUseCase") as MockUC:
        MockUC.return_value.execute = AsyncMock(
            side_effect=ReportNotFoundError(_ANALYSIS_ID)
        )
        response = await client.get(f"/reports/{_ANALYSIS_ID}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


async def test_get_report_response_structure(client, mock_report):
    """Verify all required fields are present in the response."""
    with patch("app.presentation.routes.ReportRepository"), \
         patch("app.presentation.routes.GetReportUseCase") as MockUC:
        MockUC.return_value.execute = AsyncMock(return_value=mock_report)

        response = await client.get(f"/reports/{_ANALYSIS_ID}")

    required_keys = {"analysis_id", "summary", "components", "risks", "recommendations", "created_at"}
    assert required_keys.issubset(response.json().keys())


async def test_get_report_components_is_list(client, mock_report):
    with patch("app.presentation.routes.ReportRepository"), \
         patch("app.presentation.routes.GetReportUseCase") as MockUC:
        MockUC.return_value.execute = AsyncMock(return_value=mock_report)
        response = await client.get(f"/reports/{_ANALYSIS_ID}")

    data = response.json()
    assert isinstance(data["components"], list)
    assert isinstance(data["risks"], list)
    assert isinstance(data["recommendations"], list)
