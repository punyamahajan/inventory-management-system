# Inventory Management API

A containerized REST API for managing product inventory. It provides authenticated category, product, and stock operations backed by PostgreSQL, with automated tests, API documentation, health checking, and operational logging.

## Technology stack

- Python 3.10+ (the Docker image uses Python 3.12)
- Django 5.2 and Django REST Framework
- PostgreSQL 16
- Gunicorn
- OpenAPI documentation with drf-spectacular
- Docker and Docker Compose
- GitHub Actions and GitHub Container Registry (GHCR)

## Functionality

- Create, list, retrieve, update, and delete categories and products
- Search, filter, and order inventory data
- Record stock movements and perform dedicated stock-in and stock-out operations
- Reject stock-out requests that exceed available inventory
- Identify products at or below their reorder level
- Protect inventory endpoints with DRF Session or Basic Authentication
- Expose Swagger UI, ReDoc, and the OpenAPI schema

## API endpoints

All inventory endpoints require authentication. The health endpoint is public.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET`, `POST` | `/api/categories/` | List or create categories |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/categories/{id}/` | Manage a category |
| `GET`, `POST` | `/api/products/` | List or create products |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/products/{id}/` | Manage a product |
| `GET` | `/api/products/low-stock/` | List products requiring reorder |
| `GET`, `POST` | `/api/stock-movements/` | List or record stock movements |
| `POST` | `/api/products/{id}/stock-in/` | Add product stock |
| `POST` | `/api/products/{id}/stock-out/` | Remove product stock |
| `GET` | `/health/` | Check application and PostgreSQL health |

Example requests using Basic Authentication:

```bash
curl -u <username>:<password> http://localhost:8000/api/products/

curl -u <username>:<password> \
  -H "Content-Type: application/json" \
  -d '{"quantity": 5, "notes": "Warehouse receipt"}' \
  http://localhost:8000/api/products/1/stock-in/

curl http://localhost:8000/health/
```

A healthy response is HTTP 200:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

The health check executes a query through Django's database connection. A database failure returns HTTP 503 with an unhealthy status.

## API documentation

With the application running:

- Swagger UI: <http://localhost:8000/api/docs/>
- ReDoc: <http://localhost:8000/api/redoc/>
- OpenAPI schema: <http://localhost:8000/api/schema/>

## Local setup with Docker Compose

1. Create the environment file:

   ```bash
   cp .env.example .env
   ```

2. Replace the example `SECRET_KEY` and database password in `.env` with local values.

3. Build and start the application and PostgreSQL:

   ```bash
   docker compose up --build
   ```

The API is available at <http://localhost:8000/>. The application container waits for PostgreSQL, applies migrations, collects static files, and starts Gunicorn.

Useful commands:

```bash
# Run the automated suite
docker compose exec app python manage.py test elevate

# Create or manage an application user
docker compose exec app python manage.py createsuperuser

# Stop the services
docker compose down
```

## Tests and continuous integration

The automated Django suite contains **21 tests** covering inventory operations, permissions, health checking, database failure handling, and important logging behavior.

GitHub Actions runs the suite with Python 3.10 and a PostgreSQL 16 service for pushes and pull requests targeting `main`. The Docker image is built and pushed to GHCR only after the tests pass.

## Reliability and operations

- `/health/` verifies real PostgreSQL connectivity and returns HTTP 503 when unavailable.
- Docker Compose checks `/health/` and marks the application container healthy only after an HTTP 200 response.
- PostgreSQL has its own `pg_isready` healthcheck, and the application waits for it before starting.
- Structured application logging uses the named `elevate` logger and writes container-friendly console output with level, timestamp, logger name, and message.
- Operational logs cover successful health checks, stock-in, stock-out, insufficient-stock warnings, and database health failures. Product identifiers, SKUs, and quantities are included where useful; secrets and credentials are not logged.
- Stock-out validation prevents inventory from becoming negative.
- CI prevents image publishing when the test job fails.

This repository does not currently include AWS deployment, Nginx, monitoring dashboards, or other production hosting infrastructure.

## Operational verification

With the application running, verify the health endpoint, API availability, and database connectivity:

```bash
python scripts/verify_system.py
python scripts/verify_system.py --base-url https://inventory.example.com
```

The script uses only the Python standard library, prints a PASS or FAIL for each check, and returns a nonzero exit code if verification fails. `INVENTORY_API_URL` can also set the target base URL.

## Project structure

```text
inventory-management-api/
|-- .github/workflows/docker-build.yml  # Test and container-image CI
|-- config/
|   |-- settings.py                     # Django, database, DRF, and logging settings
|   `-- urls.py                         # Project-level routes and API docs
|-- elevate/
|   |-- models.py                       # Category, Product, and StockMovement models
|   |-- serializers.py                  # Validation and API representations
|   |-- views.py                        # Inventory and health endpoints
|   |-- urls.py                         # Application routes
|   `-- tests.py                        # Automated API test suite
|-- docker-compose.yml                  # Application/PostgreSQL services and healthchecks
|-- Dockerfile                          # Application image
|-- entrypoint.sh                       # Container startup sequence
|-- manage.py
|-- scripts/verify_system.py            # Operational deployment verification
`-- requirements.txt
```

## Engineering focus

The project emphasizes predictable inventory rules, authenticated API access, database-backed readiness checks, observable operational events, repeatable containerized setup, and a test-gated image build. Production hosting infrastructure is intentionally outside the current scope.
