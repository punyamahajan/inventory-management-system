# Inventory Management System

A production-ready inventory management backend built with **Django REST Framework, PostgreSQL, Docker, Nginx, and GitHub Actions**.

The system provides authenticated REST APIs for managing products, categories, stock movements, and inventory levels, with database-backed health checks, structured logging, automated testing, API documentation, containerization, and cloud deployment.

---

## 🚀 Live Deployment

The application is deployed on **Google Cloud Compute Engine** using Docker Compose and Nginx.

| Service | URL |
|---|---|
| ❤️ Health Check | `http://34.131.159.227/health/` |
| 📚 API Documentation | `http://34.131.159.227/api/docs/` |
| 🔐 Django Admin | `http://34.131.159.227/admin/` |

> **Note:** The deployment currently uses HTTP rather than HTTPS.

---

## ✨ Key Features

### 📦 Inventory Management
- Create, update, retrieve, and delete products
- Product categorization
- SKU-based product identification
- Product pricing and stock tracking
- Configurable reorder levels
- Automatic low-stock detection
- Product status management

### 🔄 Stock Operations
- Stock-in operations
- Stock-out operations
- Stock adjustments
- Stock movement history
- Validation against insufficient inventory
- Automatic product stock updates

### 🔐 Authentication & Security
- Authenticated inventory APIs
- Django REST Framework authentication
- Protected inventory operations
- Environment-based configuration
- PostgreSQL credentials stored outside source code
- PostgreSQL is not publicly exposed
- Django application port is restricted to localhost on the production VM
- Nginx acts as the public entry point

### 🩺 Health & Reliability
- Dedicated `/health/` endpoint
- Real database connectivity check
- HTTP `503` response when the database is unavailable
- Docker health checks
- PostgreSQL readiness checks
- Structured application logging
- Automated test coverage for critical functionality

### 📖 API Documentation
Interactive OpenAPI/Swagger documentation is available through:

`/api/docs/`

This makes the API easier to test, integrate, and consume from future clients such as React applications, mobile applications, or external services.

---

# 🏗️ System Architecture

```text
                         INTERNET
                            │
                            ▼
                ┌──────────────────────┐
                │   Google Cloud VM    │
                │   Compute Engine     │
                │                      │
                │      Nginx :80       │
                │   Reverse Proxy      │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   Django REST API    │
                │   + Gunicorn         │
                │                      │
                │   Port 8000          │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │     PostgreSQL       │
                │      Database        │
                │                      │
                │   Docker Internal    │
                │      Network         │
                └──────────────────────┘
```

### Production Architecture

The application follows a layered architecture:

**Client → Nginx → Django REST API → PostgreSQL**

Nginx serves as the public reverse proxy while the Django application runs behind it. PostgreSQL remains inside the Docker network and is not exposed directly to the internet.

---

# 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Backend | Django 5.2.7 |
| API | Django REST Framework 3.16.1 |
| Database | PostgreSQL 16 |
| API Documentation | drf-spectacular / OpenAPI |
| Web Server | Gunicorn |
| Reverse Proxy | Nginx |
| Containerization | Docker |
| Orchestration | Docker Compose |
| Testing | Django Test Framework |
| CI | GitHub Actions |
| Cloud | Google Cloud Compute Engine |
| Static Files | WhiteNoise |
| Filtering | django-filter |
| Language | Python |

---

# 📁 Project Structure

```text
inventory-management-system/
│
├── .github/
│   └── workflows/
│       └── docker-build.yml
│
├── elevate/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── scripts/
│   └── verify_system.py
│
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

# 🗄️ Database Design

The system uses PostgreSQL as its persistent relational database.

### Category

Stores product categories.

```text
Category
├── id
├── name
├── description
├── created_at
└── updated_at
```

### Product

Stores inventory items.

```text
Product
├── id
├── sku
├── name
├── description
├── category
├── price
├── stock_quantity
├── reorder_level
├── status
├── created_at
└── updated_at
```

### Stock Movement

Tracks changes to inventory.

```text
StockMovement
├── id
├── product
├── movement_type
├── quantity
├── notes
└── timestamp
```

### Relationships

```text
Category
    │
    │ 1
    ▼
Product
    │
    │ 1
    ▼
StockMovement
```

A category can contain multiple products, while each stock movement belongs to a specific product.

---

# 🔌 API Endpoints

## Health

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health/` | Check application and database health |

Example response:

```json
{
    "status": "healthy",
    "database": "connected"
}
```

The health endpoint performs an actual database connectivity check rather than simply confirming that the Django process is running.

---

## Products

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/products/` | List products |
| POST | `/api/products/` | Create product |
| GET | `/api/products/{id}/` | Retrieve product |
| PUT | `/api/products/{id}/` | Update product |
| PATCH | `/api/products/{id}/` | Partially update product |
| DELETE | `/api/products/{id}/` | Delete product |

### Product Filtering

The API supports filtering and searching capabilities such as:

- Search by product information
- Filter by category
- Filter by status
- Order results
- Identify low-stock products

---

## Stock Operations

The API provides dedicated operations for inventory changes.

```text
Stock In
   │
   ▼
Product Stock ──────► Increased

Stock Out
   │
   ▼
Product Stock ──────► Decreased

Adjustment
   │
   ▼
Product Stock ──────► Corrected
```

Stock-out operations validate available inventory before modifying the product quantity.

---

# 🔒 Security Design

Several production-oriented security decisions are implemented.

### Database Isolation

PostgreSQL is not exposed directly to the public internet.

```text
Internet
   │
   ▼
Nginx :80
   │
   ▼
Django :8000
   │
   ▼
PostgreSQL
   │
   └── Internal Docker Network
```

### Application Port Protection

The Django application is bound to localhost on the production VM:

```yaml
127.0.0.1:8000:8000
```

This prevents direct public access to the application port.

### Environment Variables

Sensitive configuration such as:

- `SECRET_KEY`
- Database credentials
- Debug configuration
- Allowed hosts

is provided through environment variables rather than committed to Git.

A `.env.example` file is included for configuration reference.

---

# 🐳 Docker

The application is containerized using Docker.

### Application Container

The application container runs the Django REST API using Gunicorn.

### Database Container

PostgreSQL runs as a separate container with persistent storage through a Docker named volume.

### Docker Compose

The services are connected through an internal Docker network.

```text
┌───────────────────────────────┐
│        Docker Compose         │
│                               │
│  ┌─────────────┐              │
│  │ Django API  │              │
│  │ + Gunicorn  │              │
│  └──────┬──────┘              │
│         │                     │
│         ▼                     │
│  ┌─────────────┐              │
│  │ PostgreSQL  │              │
│  │     16      │              │
│  └─────────────┘              │
│                               │
└───────────────────────────────┘
```

---

# ☁️ Cloud Deployment

The application is deployed using:

**Google Cloud Compute Engine + Docker Compose + Nginx**

### Infrastructure

- Google Cloud Compute Engine VM
- Debian Linux
- Docker
- Docker Compose
- Nginx
- PostgreSQL 16
- Gunicorn
- Django REST Framework

### Deployment Flow

```text
GitHub Repository
       │
       ▼
Google Cloud Compute Engine
       │
       ▼
Docker Compose
       │
       ├───────────────┐
       ▼               ▼
 Django API       PostgreSQL
       │
       ▼
    Gunicorn
       │
       ▼
     Nginx
       │
       ▼
    Internet
```

The production application is served through Nginx, while the database remains private within the Docker network.

---

# 🔁 CI/CD

GitHub Actions is used to automate validation of the project.

The workflow includes:

```text
Git Push
   │
   ▼
GitHub Actions
   │
   ├── Install dependencies
   │
   ├── Start PostgreSQL
   │
   ├── Run Django tests
   │
   ├── Build Docker image
   │
   └── Push image
```

The Docker build/publish stage is dependent on the test stage, preventing a failing test suite from proceeding through the image workflow.

---

# 🧪 Testing

The project includes automated Django tests covering important API and reliability functionality.

Current test suite:

```text
21 tests
```

Run the tests locally:

```bash
python manage.py test elevate
```

Expected result:

```text
Ran 21 tests
OK
```

The test suite covers areas including:

- Product functionality
- Inventory operations
- Authentication
- Stock validation
- Health endpoint
- Database availability behavior

---

# 🩺 System Verification

A lightweight verification script is included:

```bash
python scripts/verify_system.py
```

It performs system-level checks and reports PASS/FAIL results for key application functionality.

The script is intentionally implemented using the Python standard library rather than requiring additional monitoring infrastructure.

---

# 📊 Health Monitoring

The `/health/` endpoint is designed for application availability checks.

### Healthy

```json
{
    "status": "healthy",
    "database": "connected"
}
```

### Database Failure

If the database cannot be reached, the endpoint returns an HTTP `503 Service Unavailable` response.

This allows infrastructure or monitoring systems to distinguish between:

```text
Application is running
        +
Database is available
```

and:

```text
Application is running
        +
Database is unavailable
```

---

# 📝 Logging

The application uses structured application logging for important operational events.

Logging is implemented for areas such as:

- Health-check success/failure
- Stock operations
- Application events

Sensitive information such as passwords, secrets, and authentication headers is not intentionally written to application logs.

---

# ⚙️ Local Development

## 1. Clone the Repository

```bash
git clone https://github.com/punyamahajan/inventory-management-system.git

cd inventory-management-system
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file based on:

```text
.env.example
```

Example:

```env
DEBUG=True
SECRET_KEY=your-secret-key

ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=inventory_db
DB_USER=inventory_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

> Never commit your actual `.env` file to Git.

---

# 🐘 Running PostgreSQL

If PostgreSQL is installed locally, make sure the PostgreSQL server is running and the configured database exists.

Alternatively, use Docker Compose to start the database:

```bash
docker compose up -d db
```

---

# ▶️ Run the Application

Apply migrations:

```bash
python manage.py migrate
```

Collect static files:

```bash
python manage.py collectstatic --noinput
```

Start the development server:

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

---

# 📚 API Documentation

Once the application is running, open:

```text
http://127.0.0.1:8000/api/docs/
```

The documentation provides an interactive interface for exploring and testing the REST API.

---

# 🔐 Django Admin

The project includes Django Admin for internal management and administration.

Create an administrator:

```bash
python manage.py createsuperuser
```

Then open:

```text
http://127.0.0.1:8000/admin/
```

---

# 🐳 Run Everything with Docker

Build and start the application:

```bash
docker compose up -d --build
```

Check running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f app
```

Stop the application:

```bash
docker compose down
```

---

# 🔄 Database Migrations with Docker

Run migrations inside the application container:

```bash
docker compose exec app python manage.py migrate
```

Collect static files:

```bash
docker compose exec app python manage.py collectstatic --noinput
```

---

# 🧠 Design Decisions

## Why PostgreSQL?

PostgreSQL provides:

- Strong relational data modeling
- Transaction support
- Data integrity
- Production-grade persistence
- Efficient querying and indexing

It is well suited for an inventory system where products and stock movements have clear relational relationships.

---

## Why Docker?

Docker provides a reproducible runtime environment for:

- Django
- PostgreSQL
- Gunicorn
- Application dependencies

This reduces environment-related differences between development and deployment.

---

## Why Nginx?

Nginx provides a dedicated public-facing HTTP layer in front of the Django application.

It allows the architecture to separate:

```text
Public HTTP Traffic
        ↓
      Nginx
        ↓
   Django/Gunicorn
```

It also allows the Django application itself to remain inaccessible directly from the public internet.

---

## Why Gunicorn?

Gunicorn provides a production-oriented WSGI server for running the Django application rather than relying on Django's development server.

---

## Why Health Checks?

A process being alive does not necessarily mean the application is operational.

The health endpoint verifies the application's ability to communicate with the PostgreSQL database.

This makes it useful for:

- Deployment validation
- Container health checks
- Operational monitoring
- Troubleshooting

---

# 📈 Scalability Considerations

The current architecture provides a foundation that can be extended as traffic and operational requirements increase.

Potential future improvements include:

- HTTPS with TLS certificates
- Managed PostgreSQL
- Load balancing
- Horizontal application scaling
- Centralized monitoring
- Metrics and alerting
- Redis-based caching
- Background task processing
- Kubernetes-based orchestration
- Infrastructure-as-Code

These are **future improvements**, not currently implemented components.

---

# 🔮 Future Enhancements

### Security
- HTTPS / TLS
- Rate limiting
- Improved authentication mechanisms
- Secret management through a cloud secret manager

### Performance
- Redis caching
- Database query optimization
- Connection pooling
- Pagination optimization

### Observability
- Application metrics
- Centralized logs
- Alerting
- Performance monitoring

### Infrastructure
- Managed PostgreSQL
- Load balancer
- Automated production deployments
- Infrastructure as Code

---

# 📌 Project Highlights

| Area | Implementation |
|---|---|
| Backend | Django REST Framework |
| Database | PostgreSQL |
| API | RESTful |
| Authentication | Implemented |
| API Documentation | OpenAPI / Swagger |
| Containerization | Docker |
| Service Orchestration | Docker Compose |
| Reverse Proxy | Nginx |
| Production Server | Gunicorn |
| Health Checks | Implemented |
| Structured Logging | Implemented |
| Automated Tests | 21 tests |
| CI | GitHub Actions |
| Cloud Deployment | Google Cloud Compute Engine |
| Database Exposure | Internal only |

---

# 🎯 Engineering Focus

This project was designed with a focus on practical backend and system engineering principles rather than simply building CRUD endpoints.

Key engineering concerns addressed include:

- API design
- Database modeling
- Data validation
- Authentication
- Inventory consistency
- Failure handling
- Health checks
- Logging
- Containerization
- Service isolation
- Reverse proxy architecture
- Automated testing
- CI workflows
- Cloud deployment
- Production configuration

---

# 👨‍💻 Author

**Punya Mahajan**

B.Tech Computer Science & Engineering

GitHub: [@punyamahajan](https://github.com/punyamahajan)

---

# 📄 License

This project is intended for educational and portfolio purposes.

---

## ⭐ Project Summary

**Inventory Management System** is a containerized Django REST API designed to demonstrate production-oriented backend engineering practices.

It combines:

```text
Django REST Framework
        +
PostgreSQL
        +
Docker
        +
Gunicorn
        +
Nginx
        +
GitHub Actions
        +
Google Cloud
```

to provide a reliable foundation for inventory management through documented and authenticated REST APIs.