# fiap-hackathon-report-service

Armazena e serve relatórios técnicos gerados pelo processing-service após a análise de diagramas de arquitetura.

## Responsabilidade

- Persistir relatórios técnicos recebidos do processing-service (idempotente: não duplica relatórios para o mesmo `analysis_id`)
- Disponibilizar relatórios para consulta por `analysis_id`
- Retornar componentes identificados, riscos detectados e recomendações

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/reports` | Salva um novo relatório técnico (chamado pelo processing-service) |
| `GET` | `/reports/{analysis_id}` | Retorna o relatório de uma análise específica |
| `GET` | `/health` | Health check |

### Estrutura do relatório

```json
{
  "analysis_id": "uuid",
  "summary": "Foram identificados N componentes arquiteturais.",
  "components": ["api gateway", "database", "redis"],
  "risks": ["Ausência de load balancer."],
  "recommendations": ["Implementar circuit breaker."],
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DATABASE_URL` | `postgresql+asyncpg://report_user:report_pass@localhost:5432/report_db` | Banco de dados PostgreSQL |
| `SERVICE_NAME` | `report-service` | Nome do serviço (usado em logs) |
| `LOG_LEVEL` | `INFO` | Nível de log |

## Como rodar localmente (sem Docker)

```bash
# Pré-requisito: PostgreSQL em execução

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Ajuste DATABASE_URL

uvicorn app.main:app --port 8003 --reload
```

## Como rodar com Docker (standalone)

```bash
docker build -t fiap-hackathon/report-service .
docker run --rm -p 8003:8003 \
  -e DATABASE_URL=postgresql+asyncpg://report_user:report_pass@host.docker.internal:5432/report_db \
  fiap-hackathon/report-service
```

## Como rodar os testes

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

## Arquitetura completa e orquestração

Para rodar o sistema completo (todos os serviços + infraestrutura), consulte o repositório de documentação:

**[fiap-hackathon-docs](../fiap-hackathon-docs)** — contém `docker-compose.yml`, `.env.example` e instruções de setup do ambiente completo.
