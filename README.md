# Sentinel - Infrastructure Health Monitor

A robust, production-ready service for monitoring endpoint availability with real-time metrics, alerting, and historical data tracking.

## Features

- **Async Health Checking** - Parallel monitoring of multiple endpoints
- **REST API** - Full CRUD operations for monitor management
- **PostgreSQL Storage** - Persistent health check history
- **Prometheus Metrics** - Built-in observability
- **Alerting System** - Pluggable alert providers (Slack, Email, Discord)
- **Docker Ready** - Fully containerized with Docker Compose
- **CI/CD Pipeline** - Automated testing and quality checks

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   FastAPI   │────────▶│  PostgreSQL  │◀────────│   Worker    │
│  (REST API) │         │  (Metrics)   │         │ (Scheduler) │
└─────────────┘         └──────────────┘         └─────────────┘
      │                                                  │
      │                                                  │
      ▼                                                  ▼
┌─────────────┐                                  ┌─────────────┐
│ Prometheus  │                                  │  Monitored  │
│  /metrics   │                                  │  Endpoints  │
└─────────────┘                                  └─────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Poetry (recommended) or pip

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sentinel
   ```

2. **Install dependencies**
   ```bash
   poetry install
   # or
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

5. **Run database migrations**
   ```bash
   poetry run alembic upgrade head
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Metrics: http://localhost:8000/metrics

## Project Structure

```
sentinel/
├── app/
│   ├── main.py              # FastAPI application
│   ├── worker.py            # Background monitoring service
│   ├── config.py            # Configuration management
│   ├── core/                # Business logic
│   ├── db/                  # Database models & repositories
│   ├── api/                 # API routes
│   └── services/            # Application services
├── tests/                   # Test suite
├── alembic/                 # Database migrations
├── scripts/                 # Utility scripts
└── docker-compose.yml       # Container orchestration
```

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_checker.py
```

## Development

### Code Quality

```bash
# Format code
poetry run black app tests

# Lint
poetry run ruff check app tests

# Type checking
poetry run mypy app
```

### Database Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback
poetry run alembic downgrade -1
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/v1/monitors` | List all monitors |
| POST | `/api/v1/monitors` | Create new monitor |
| GET | `/api/v1/monitors/{id}` | Get monitor details |
| PUT | `/api/v1/monitors/{id}` | Update monitor |
| DELETE | `/api/v1/monitors/{id}` | Delete monitor |
| GET | `/api/v1/monitors/{id}/history` | Get check history |

## Security

- API Key authentication (configurable)
- Input validation with Pydantic
- Rate limiting on sensitive endpoints
- Docker secrets support for production

## Monitoring

The service exposes Prometheus metrics at `/metrics`:

- `sentinel_checks_total` - Total health checks performed
- `sentinel_latency_seconds` - Response time histogram
- `sentinel_monitors_up` - Current number of UP monitors

## Deployment

### Docker Compose (Production)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

See `.env.example` for all available configuration options.

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Contact

Sebastian Lodin - [GitHub](https://github.com/Se8o)
