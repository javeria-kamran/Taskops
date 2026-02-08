# Naz Todo - Backend API

FastAPI backend for the Naz Todo application with JWT authentication, PostgreSQL database, and comprehensive task management.

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL (Neon Serverless)
- **ORM**: SQLModel (async)
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Testing**: pytest with async support
- **Python**: 3.13+

## Project Structure

```
backend/
├── alembic/                    # Database migrations
│   └── versions/               # Migration files
├── app/
│   ├── models/                 # SQLModel database models
│   │   ├── user.py            # User model
│   │   └── task.py            # Task model
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── user.py            # User schemas
│   │   └── task.py            # Task schemas
│   ├── routers/                # API route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   └── tasks.py           # Task CRUD endpoints
│   ├── dependencies/           # FastAPI dependencies
│   │   └── auth.py            # JWT authentication dependencies
│   ├── middleware/             # Custom middleware
│   │   └── auth.py            # Auth middleware
│   ├── config.py              # Application configuration
│   ├── database.py            # Database connection setup
│   └── main.py                # FastAPI application entry point
├── tests/                      # Test suite
│   ├── conftest.py            # Pytest fixtures
│   ├── test_auth.py           # Authentication tests
│   └── test_tasks.py          # Task management tests
├── .env.example               # Environment variables template
├── alembic.ini                # Alembic configuration
├── pyproject.toml             # Project dependencies and config
└── requirements.txt           # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.13+
- UV (Python package manager)
- PostgreSQL database (Neon recommended)

### Installation

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment with UV**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and update:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string
   - `BETTER_AUTH_SECRET`: A secure secret key (min 32 characters)
   - `ALLOWED_ORIGINS`: Frontend URL (default: http://localhost:3000)

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at: http://localhost:8000

## API Documentation

Interactive API documentation is automatically available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Login user
- `GET /api/auth/session` - Get current session
- `POST /api/auth/signout` - Logout user
- `GET /api/auth/me` - Get current user info

### Tasks (Protected - Requires Authentication)

- `POST /api/tasks` - Create new task
- `GET /api/tasks` - Get all user's tasks (with optional ?completed filter)
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

## Authentication

All task endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

Get a token by signing up or signing in through the auth endpoints.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks.py

# Run with verbose output
pytest -v
```

## Database Migrations

### Create a new migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migration

```bash
alembic downgrade -1
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `BETTER_AUTH_SECRET` | JWT secret key (min 32 chars) | Required |
| `JWT_ALGORITHM` | JWT algorithm | HS256 |
| `JWT_EXPIRATION_MINUTES` | Token expiration time | 10080 (7 days) |
| `ALLOWED_ORIGINS` | CORS allowed origins | http://localhost:3000 |
| `ENVIRONMENT` | Environment name | development |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |

## Production Deployment

### Using Docker

```bash
docker build -t naz-todo-backend .
docker run -p 8000:8000 --env-file .env naz-todo-backend
```

### Using Gunicorn

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Configuration

For production:
- Set `ENVIRONMENT=production`
- Use a strong `BETTER_AUTH_SECRET` (generate with: `openssl rand -hex 32`)
- Enable database SSL (`?sslmode=require` in DATABASE_URL)
- Configure CORS with actual frontend domain

## Code Quality

### Linting

```bash
# Run ruff
ruff check .

# Auto-fix issues
ruff check --fix .
```

### Formatting

```bash
# Format with black
black .
```

## Features

- ✅ JWT-based authentication
- ✅ User isolation (users only see their own tasks)
- ✅ Async PostgreSQL with SQLModel
- ✅ Comprehensive input validation
- ✅ Database migrations with Alembic
- ✅ CORS configuration
- ✅ Comprehensive test coverage
- ✅ API documentation (Swagger/ReDoc)

## License

MIT
