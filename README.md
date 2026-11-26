# URL Shortener Service

A URL shortener microservice built with FastAPI, PostgreSQL, and Redis. This service provides URL shortening with user authentication, analytics, and tier-based access control.

## Overview

This project implements a URL shortening system. It features user authentication with JWT tokens, tier-based access control (FREE, PREMIUM, ADMIN), click tracking and analytics, custom URL aliases, and rate limiting. The service uses PostgreSQL for persistent storage and Redis for caching.

## Key Features

- Shorten long URLs to 6-character alphanumeric codes
- User registration and authentication with JWT tokens
- Tier-based access control (FREE, PREMIUM, ADMIN)
- Custom URL aliases for premium users
- Click tracking with IP address, user agent, and referrer
- Analytics endpoint for premium users
- Automatic deduplication: identical URLs return the same short code
- URL expiration support
- Fast 307 temporary redirects to original URLs
- Health check endpoint monitoring PostgreSQL and Redis
- Rate limiting on login endpoint
- Interactive API documentation via Swagger UI
- Docker Compose setup with Redis Insight for monitoring

## Technology Stack

| Component             | Technology                             |
| --------------------- | -------------------------------------- |
| Framework             | FastAPI 0.162.x                        |
| Language              | Python 3.12+                           |
| Database              | PostgreSQL 16                          |
| Cache                 | Redis 7                                |
| ORM                   | SQLAlchemy 2.x (async)                 |
| Migrations            | Alembic                                |
| ID Generation         | nanoid                                 |
| Authentication        | JWT (PyJWT)                            |
| Password Hashing      | Argon2 (pwdlib)                        |
| Rate Limiting         | fastapi-limiter                        |
| Dependency Management | Poetry                                 |
| Testing               | pytest, pytest-asyncio, testcontainers |
| Containerization      | Docker & Docker Compose                |

## Project Structure

```
.
├── alembic/                      # Database migrations
├── app/
│   ├── core/                     # Configuration, dependencies, utilities
│   ├── middleware/               # Request logging
│   ├── models/                   # SQLAlchemy models
│   ├── repositories/             # Data access layer
│   ├── routes/                   # API endpoints
│   ├── schemas/                  # Pydantic models
│   └── services/                 # Business logic
├── tests/                        # Integration tests
├── .env.example                  # Environment variable template
├── Dockerfile                    # Multi-stage Docker build
├── docker-compose.yml            # Docker Compose orchestration
├── alembic.ini                   # Alembic configuration
└── pyproject.toml                # Poetry dependencies
```

## Prerequisites

- Python 3.12 or higher
- Poetry for dependency management
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL 16 and Redis 7 (if running locally without Docker)

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

4. Edit `.env` with your configuration (see Environment Variables section)

5. Run database migrations:

```bash
poetry run alembic upgrade head
```

### Docker Deployment

The service includes a multi-stage Dockerfile and docker-compose configuration.

## Environment Variables

| Variable                    | Description                        | Default     | Required |
| --------------------------- | ---------------------------------- | ----------- | -------- |
| `APP_NAME`                  | Application name                   | -           | Yes      |
| `APP_SUMMARY`               | Application description            | -           | Yes      |
| `APP_BASE_URL`              | Base URL for API endpoints         | -           | Yes      |
| `APP_DOMAIN`                | Domain for constructing short URLs | -           | Yes      |
| `REDIS_HOST`                | Redis server host                  | `localhost` | No       |
| `REDIS_PORT`                | Redis server port                  | `6379`      | No       |
| `REDIS_DB`                  | Redis database number              | `0`         | No       |
| `PG_HOST`                   | PostgreSQL server host             | -           | Yes      |
| `PG_USER`                   | PostgreSQL username                | -           | Yes      |
| `PG_PASSWORD`               | PostgreSQL password                | -           | Yes      |
| `PG_PORT`                   | PostgreSQL server port             | -           | Yes      |
| `PG_DBNAME`                 | PostgreSQL database name           | -           | Yes      |
| `JWT_SECRET_KEY`            | JWT signing secret                 | -           | Yes      |
| `JWT_ALGORITHM`             | JWT algorithm                      | `HS256`     | No       |
| `ACCESS_TOKEN_EXPIRE_DAYS`  | Access token lifetime in days      | `7`         | No       |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime in days     | `1`         | No       |

## Database Migrations

The project uses Alembic for database migrations.

Run migrations:

```bash
poetry run alembic upgrade head
```

Create a new migration:

```bash
poetry run alembic revision --autogenerate -m "description"
```

Rollback to previous version:

```bash
poetry run alembic downgrade -1
```

## Running the Application

### Using Docker Compose (Recommended)

Start the application, PostgreSQL, Redis, and Redis Insight:

```bash
docker-compose up --build
```

The service will be available at `http://localhost:8000`.
Redis Insight UI will be available at `http://localhost:5540`.

### Local Development

1. Ensure PostgreSQL and Redis are running locally
2. Activate the virtual environment:

```bash
poetry shell
```

3. Run database migrations:

```bash
alembic upgrade head
```

4. Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API documentation will be available at `http://localhost:8000/docs`.

## How the URL Shortener Works

The URL shortening process involves these steps:

1. **User Authentication**:
   - Users register with email and password
   - Passwords are hashed using Argon2
   - JWT access and refresh tokens are issued on login
   - Tokens are validated on protected endpoints

2. **Shortening a URL**:
   - Authenticated user sends a POST request with a long URL
   - Service checks if the URL already exists for the user
   - If found, returns the existing short code (idempotent)
   - If not found, generates a new 6-character alphanumeric code
   - Stores the mapping in PostgreSQL with user ownership
   - Returns the full short URL (domain + code)

3. **Redirecting**:
   - Client accesses the short URL via a code
   - Service logs the click (IP, user agent, referrer)
   - Validates the URL is active and not expired
   - Returns a 307 redirect to the original URL
   - When accessed via Swagger UI, returns HTTP 200 with JSON

4. **Tier-Based Access**:
   - FREE tier: 10 active URLs, no custom aliases
   - PREMIUM tier: unlimited URLs, custom aliases, analytics access
   - ADMIN tier: all privileges plus admin endpoints

## API Documentation

### Health Check

**Endpoint:** `GET /health`

Returns service status and health of PostgreSQL and Redis dependencies.

### Authentication

**Register:** `POST /api/v1/auth/register`

- Request: `{"email": "user@example.com", "password": "securepassword123"}`
- Response: User object with id, email, is_premium, tier

**Login:** `POST /api/v1/auth/login`

- Request: `{"email": "user@example.com", "password": "securepassword123"}`
- Response: JWT access_token, refresh_token, token_type
- Rate Limit: 5 requests per minute

**Refresh Token:** `POST /api/v1/auth/refresh`

- Request: `{"refresh_token": "token"}`
- Response: New access and refresh tokens

**Get Current User:** `GET /api/v1/auth/me`

- Headers: `Authorization: Bearer {access_token}`
- Response: Current user object

### URL Management

**Create Short URL:** `POST /api/v1/urls`

- Headers: `Authorization: Bearer {access_token}`
- Request: `{"original_url": "https://example.com", "custom_alias": "mylink", "title": "My Link", "description": "desc", "favicon": "url"}`
- Response: ShortUrl object with id, original_url, short_code, custom_alias, is_active, expires_at, title, description, favicon, click_count, owner_id
- Note: Returns 200 with `Idempotent-Replayed: true` if URL already exists

**List User URLs:** `GET /api/v1/urls`

- Headers: `Authorization: Bearer {access_token}`
- Response: Array of ShortUrl objects

**Get URL Details:** `GET /api/v1/urls/{short_code}`

- Headers: `Authorization: Bearer {access_token}`
- Response: ShortUrl object

**Update URL:** `PUT /api/v1/urls/{short_code}`

- Headers: `Authorization: Bearer {access_token}`
- Request: `{"custom_alias": "newalias", "title": "Updated", "description": "updated"}`
- Response: Updated ShortUrl object

**Deactivate URL:** `DELETE /api/v1/urls/{short_code}`

- Headers: `Authorization: Bearer {access_token}`
- Response: 204 No Content

**Redirect to Long URL:** `GET /{short_code}`

- Returns HTTP 307 redirect to original URL
- Logs click data (IP, user agent, referrer)
- Returns HTTP 200 with JSON when accessed via Swagger UI

**Admin Endpoints (ADMIN tier only):**

- `GET /api/v1/urls/active` - List all active URLs
- `GET /api/v1/urls/expired` - List all expired URLs
- `GET /api/v1/urls/popular` - List URLs sorted by click count
- Response: Array of ShortUrlWithOwnerResponse objects

### Analytics

**Get URL Analytics:** `GET /api/v1/analytics/{short_code}`

- Headers: `Authorization: Bearer {access_token}`
- Requires PREMIUM tier
- Response: `{"short_code": "abc123", "total_clicks": 42, "time_series": [{"date": "2024-11-25", "clicks": 10}]}`

## Database Structure

### Users Table

- id (UUID, primary key)
- email (String 250, unique)
- password_hash (String 100)
- is_premium (Boolean)
- tier (Enum: FREE, PREMIUM, ADMIN)

### Short URLs Table

- id (UUID, primary key)
- original_url (String 2048)
- short_code (String 6, unique)
- custom_alias (String 50, unique, nullable)
- is_active (Boolean)
- expires_at (DateTime, nullable)
- title (String 255, nullable)
- description (Text, nullable)
- favicon (String 2048, nullable)
- click_count (Integer)
- created_at (DateTime)
- owner_id (UUID, foreign key to users)

### Clicks Table

- id (BigInteger, primary key)
- clicked_at (DateTime)
- ip_address (String 45, nullable)
- city (String 50, nullable)
- country (String 50, nullable)
- user_agent (String 100)
- referrer (String 2048, nullable)
- short_url_id (UUID, foreign key to short_urls)

### Tags Table

- id (UUID, primary key)
- name (String 50, unique)

### Short URL Tags Association

Many-to-many relationship between short_urls and tags.

## Testing

The project uses pytest with asyncio support and testcontainers for integration testing.

Run all tests:

```bash
poetry run pytest
```

Run with coverage:

```bash
poetry run pytest --cov=app --cov-report=html
```

Run specific test file:

```bash
poetry run pytest tests/integration/test_auth.py
```

Test configuration:

- Uses testcontainers for PostgreSQL and Redis
- Alembic migrations run automatically
- Database cleaned between tests
- Async fixtures for database sessions and Redis clients

## Known Limitations and Potential Improvements

**Current Limitations:**

- Geographic location data (city, country) is stored but not populated
- No bulk URL creation or deletion
- No URL validation beyond HTTP/HTTPS scheme check
- No API key authentication (only JWT)
- No OAuth integration
- Limited to 6-character short codes
- No password reset functionality
- No email verification for registration
- Admin operations cannot be performed via API (requires direct database access)

**Potential Improvements:**

- Implement IP geolocation for click tracking
- Add bulk operations for URL management
- Add URL reachability validation before shortening
- Implement API key authentication for external integrations
- Add OAuth providers (Google, GitHub)
- Support configurable short code lengths
- Implement password reset flow
- Add email verification for registration
- Create admin API endpoints for user management
- Add webhook notifications for click events
- Implement QR code generation for short URLs
- Add URL preview/thumbnail generation
- Implement domain whitelisting/blacklisting
- Add more granular permission system
- Implement caching for frequently accessed URLs
- Add support for URL groups or folders
