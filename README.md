# URL Shortener Service

A lightweight URL shortener microservice built with FastAPI and Redis. This service accepts long URLs and returns shortened URLs that redirect to the original destination.

## Overview

This project implements a basic URL shortening system as a lab exercise. It uses Redis for efficient storage and retrieval of URL mappings, with nanoid-based code generation for short URLs. The service is containerized for easy deployment using Docker.

## Key Features

- Shorten long URLs to 6-character alphanumeric codes
- Automatic deduplication: identical URLs return the same short code
- Fast 307 temporary redirects to original URLs
- Redis-based storage for high performance
- Health check endpoint
- Interactive API documentation via Swagger UI
- Docker Compose setup for local development

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI 0.162.x |
| Language | Python 3.12+ |
| Database | Redis 7 |
| ID Generation | nanoid |
| Dependency Management | Poetry |
| Containerization | Docker & Docker Compose |

## Project Structure

```
.
├── app/
│   ├── core/
│   │   ├── config.py          # Application settings and environment variables
│   │   └── database.py        # Redis connection configuration
│   ├── routes/
│   │   └── urls.py            # API endpoint definitions
│   ├── schemas/
│   │   └── url.py             # Pydantic models for request/response
│   ├── services/
│   │   └── url_shortener_service.py  # Core URL shortening logic
│   ├── dependencies.py         # FastAPI dependency injection
│   ├── main.py                # Application entry point
│   └── utils.py               # ID generation utilities
├── .env.example               # Environment variable template
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.yml         # Docker Compose orchestration
└── pyproject.toml             # Poetry dependencies
```

## Prerequisites

- Python 3.12 or higher
- Poetry for dependency management
- Docker and Docker Compose (for containerized deployment)
- Redis 7 (if running locally without Docker)

## Installation and Setup

### Local Development

1. Clone the repository and navigate to the project directory:
```bash
cd URL_Shortener_Service
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Copy the environment example file and configure it:
```bash
cp .env.example .env
```

4. Edit `.env` with your configuration:
```bash
APP_NAME="URL Shortener Microservice"
APP_SUMMARY="An API for a url shortener microservice."
APP_BASE_URL="http://localhost:8000/api/v1"
APP_DOMAIN="http://localhost:8000"
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### Docker Deployment

The service includes a multi-stage Dockerfile and docker-compose configuration for containerized deployment.

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | - | Yes |
| `APP_SUMMARY` | Application description | - | Yes |
| `APP_BASE_URL` | Base URL for API endpoints | - | Yes |
| `APP_DOMAIN` | Domain for constructing short URLs | - | Yes |
| `REDIS_HOST` | Redis server host | `localhost` | No |
| `REDIS_PORT` | Redis server port | `6379` | No |
| `REDIS_DB` | Redis database number | `0` | No |

## Running the Application

### Using Docker Compose (Recommended)

Start the application and Redis together:

```bash
docker-compose up --build
```

The service will be available at `http://localhost:8000`.

### Local Development

1. Ensure Redis is running locally on port 6379
2. Activate the virtual environment:
```bash
poetry shell
```

3. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API documentation will be available at `http://localhost:8000/docs`.

## How the URL Shortener Works

The URL shortening process involves these steps:

1. **Shortening a URL**:
   - Client sends a POST request with a long URL
   - Service checks if the URL already exists in Redis (using a hash map)
   - If found, returns the existing short code
   - If not found, generates a new 6-character alphanumeric code using nanoid
   - Stores the mapping in Redis: one key-value pair for code→URL, and a hash entry for URL→code
   - Returns the full short URL (domain + code)

2. **Redirecting**:
   - Client accesses the short URL via a code
   - Service looks up the code in Redis
   - If found, returns a 307 redirect to the original URL
   - If not found, returns a 400 error

3. **Storage**:
   - URL→code mapping stored in Redis hash (`long_urls`)
   - Code→URL mapping stored as individual Redis keys (`url:{code}`)

## API Documentation

### Health Check

Check service status.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "Status": "Alive"
}
```

### Create Short URL

Generate a short URL for a given long URL.

**Endpoint:** `POST /api/v1/urls`

**Request Body:**
```json
{
  "url": "https://example.com/very/long/path"
}
```

**Response:**
```json
{
  "short_url": "http://localhost:8000/abc123"
}
```

**Example using curl:**
```bash
curl -X POST http://localhost:8000/api/v1/urls \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Redirect to Long URL

Redirect to the original URL using a short code.

**Endpoint:** `GET /{url_code}`

**Behavior:**
- Returns HTTP 307 redirect to the original URL
- When accessed via Swagger UI, returns HTTP 200 with JSON response

**Response (Swagger UI):**
```json
{
  "status": "success",
  "message": "Redirect intercepted for SwaggerUI or Redoc compatibility.",
  "redirect_to": "https://example.com"
}
```

**Error Response (Invalid Code):**
```json
{
  "detail": "Invalid URL"
}
```

**Example using curl:**
```bash
curl -L http://localhost:8000/abc123
```

## Database Structure

The service uses Redis with the following data structure:

| Key Type | Key Pattern | Value | Purpose |
|----------|-------------|-------|---------|
| String | `url:{code}` | Long URL | Fast lookup by short code |
| Hash Field | `long_urls` (hash) | Field: Long URL, Value: Code | Deduplication check for existing URLs |

The hash map `long_urls` prevents duplicate short codes for the same URL, while individual string keys enable fast redirects.

## Testing

This project does not currently include automated tests. Manual testing can be performed through the Swagger UI at `/docs` or using curl commands as shown in the API documentation section.

## Known Limitations and Potential Improvements

**Current Limitations:**
- No persistence beyond Redis (data lost on Redis restart unless persistence is configured)
- No authentication or rate limiting
- No analytics or click tracking
- No custom short code support
- No URL expiration/TTL
- No validation of URL reachability before shortening
- Limited to HTTP/HTTPS URLs

**Potential Improvements:**
- Add Redis persistence configuration (AOF/RDB)
- Implement rate limiting per IP or user
- Add click tracking and analytics
- Support custom short codes
- Add URL expiration with TTL
- Validate URLs before accepting them
- Add unit and integration tests
- Implement caching layer for frequently accessed URLs
- Add support for additional protocols (ftp, mailto, etc.)
- Implement user accounts and URL management
- Add API key authentication

## License

No license file is present in this repository.
