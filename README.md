# Inventory Management System

A production-oriented inventory management REST API built with Django and Django REST Framework. The system provides product and inventory operations, stock tracking, low-stock monitoring, API documentation, and containerized deployment.

## Tech Stack

- **Backend:** Python, Django, Django REST Framework
- **Database:** PostgreSQL
- **API Documentation:** OpenAPI / Swagger
- **Containerization:** Docker, Docker Compose
- **Application Server:** Gunicorn
- **Background Processing:** Celery, Redis
- **CI/CD:** GitHub Actions

## Features

- RESTful API for inventory management
- Product and category management
- Stock tracking and inventory updates
- Low-stock and reorder-level monitoring
- PostgreSQL database integration
- API schema and interactive documentation
- Dockerized application environment
- Production deployment configuration
- Background task support using Celery and Redis
- Automated Docker build through GitHub Actions

## Project Structure

```text
inventory-management-system/
│
├── .github/
│   └── workflows/
│       └── docker-build.yml
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── elevate/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
│
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── manage.py
├── requirements.txt
└── README.md
```

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/punyamahajan/inventory-management-system.git
cd inventory-management-system
```

### 2. Configure environment variables

Create a `.env` file using the provided example:

```bash
cp .env.example .env
```

Update the database and application configuration as required.

### 3. Build and start the containers

```bash
docker compose up --build
```

The application will then be available through the configured API port.

### 4. Run migrations

If required:

```bash
docker compose exec web python manage.py migrate
```

### 5. Run tests

```bash
docker compose exec web python manage.py test
```

## API Documentation

The project uses `drf-spectacular` to generate an OpenAPI schema and interactive API documentation.

Once the application is running, the configured documentation endpoints can be used to explore and test the available API operations.

## Development Workflow

The project is designed around a containerized development and deployment workflow:

```text
Code Change
     │
     ▼
Git Commit / Push
     │
     ▼
GitHub Actions
     │
     ├── Run checks
     └── Build Docker image
              │
              ▼
        Deployment Environment
```

## Engineering Focus

The project is being developed with production and systems
