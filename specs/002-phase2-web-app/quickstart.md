# Naz Todo - Quick Start Guide

Complete end-to-end setup guide to get the Naz Todo application running locally in under 10 minutes.

## Overview

Naz Todo is a full-stack task management application with:
- **Backend**: FastAPI + PostgreSQL + JWT Authentication
- **Frontend**: Next.js 16 + React 19 + Tailwind CSS
- **Database**: Neon Serverless PostgreSQL

## Prerequisites

Before starting, ensure you have:

- [x] **Python 3.13+** installed
- [x] **Node.js 18+** and npm installed
- [x] **UV** (Python package manager): `pip install uv`
- [x] **PostgreSQL database** (Neon account recommended - free tier available)
- [x] **Git** for cloning the repository

## Step 1: Database Setup (5 minutes)

### Option A: Neon (Recommended - Free)

1. Go to [neon.tech](https://neon.tech) and sign up
2. Create a new project named "naz-todo"
3. Copy the connection string (should look like):
   ```
   postgresql://user:password@ep-xxx-xxx.neon.tech/naz_todo?sslmode=require
   ```
4. Keep this connection string handy

### Option B: Local PostgreSQL

```bash
# Create database
createdb naz_todo

# Connection string will be:
postgresql://localhost/naz_todo
```

## Step 2: Backend Setup (3 minutes)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Edit `backend/.env`:

```env
# Required - paste your Neon connection string
DATABASE_URL=postgresql://your-neon-connection-string

# Required - generate with: openssl rand -hex 32
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-replace-this

# Optional - defaults are fine for local development
ALLOWED_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

Run database migrations:

```bash
alembic upgrade head
```

Start the backend server:

```bash
uvicorn app.main:app --reload
```

✅ Backend should now be running at http://localhost:8000

Verify by visiting: http://localhost:8000/docs (API documentation)

## Step 3: Frontend Setup (2 minutes)

Open a **new terminal window** and:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
DATABASE_URL=your-neon-connection-string  # Same as backend
```

Start the frontend server:

```bash
npm run dev
```

✅ Frontend should now be running at http://localhost:3000

## Step 4: Test the Application

### 1. Visit the Landing Page

Open http://localhost:3000 in your browser

### 2. Sign Up

1. Click "Get Started"
2. Fill in:
   - Name: Your Name
   - Email: test@example.com
   - Password: Test1234 (min 8 chars, 1 uppercase, 1 digit)
3. Click "Sign up"

✅ You should be redirected to the dashboard

### 3. Create a Task

1. Click "New Task" button
2. Enter:
   - Title: "My First Task"
   - Description: "Testing the app"
3. Click "Create Task"

✅ Task should be created successfully

### 4. View All Tasks

1. Click "All Tasks" in the navigation
2. You should see your task listed

### 5. Complete a Task

1. Click the checkbox next to your task
2. Task should be marked as completed with a strikethrough

### 6. Edit a Task

1. Click "Edit" on your task
2. Update the title or description
3. Click "Update Task"

✅ Changes should be saved

### 7. Delete a Task

1. Click "Delete" on your task
2. Confirm the deletion

✅ Task should be removed from the list

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError`
```bash
# Solution: Ensure virtual environment is activated
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Problem**: Database connection error
```bash
# Solution: Check DATABASE_URL in .env
# Ensure Neon database is running
# Try regenerating connection string from Neon dashboard
```

**Problem**: Migration errors
```bash
# Solution: Reset migrations
alembic downgrade base
alembic upgrade head
```

### Frontend Issues

**Problem**: `Cannot connect to backend`
```bash
# Solution: Ensure backend is running on port 8000
# Check NEXT_PUBLIC_BACKEND_URL in .env.local
```

**Problem**: Build errors
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules .next
npm install
npm run dev
```

**Problem**: Authentication errors
```bash
# Solution: Clear browser storage
# Open DevTools > Application > Clear storage
```

## Project Structure

```
Naz Todo/
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── models/        # Database models
│   │   ├── routers/       # API endpoints
│   │   ├── schemas/       # Request/response schemas
│   │   └── main.py        # App entry point
│   ├── alembic/           # Database migrations
│   ├── tests/             # Backend tests
│   └── .env               # Environment config
│
├── frontend/              # Next.js frontend
│   ├── app/              # App router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities & API client
│   ├── types/            # TypeScript types
│   └── .env.local        # Environment config
│
└── specs/                # Specifications
    └── 002-phase2-web-app/
        ├── plan.md       # Implementation plan
        ├── tasks.md      # Task breakdown
        └── spec.md       # Feature specifications
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Login user
- `GET /api/auth/session` - Get current session
- `POST /api/auth/signout` - Logout user

### Tasks (Protected)
- `POST /api/tasks` - Create task
- `GET /api/tasks` - Get all tasks
- `GET /api/tasks/{id}` - Get single task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

## Running Tests

### Backend Tests

```bash
cd backend
pytest                          # Run all tests
pytest --cov=app               # With coverage
pytest tests/test_tasks.py -v  # Specific test file
```

### Frontend Tests

```bash
cd frontend
npm test                # Run all tests
npm run test:watch     # Watch mode
```

## Development Workflow

1. **Backend changes**:
   - Edit code in `backend/app/`
   - Server auto-reloads (--reload flag)
   - Run tests: `pytest`

2. **Frontend changes**:
   - Edit code in `frontend/`
   - Browser auto-refreshes (hot reload)
   - Check types: `npx tsc --noEmit`

3. **Database changes**:
   - Edit models in `backend/app/models/`
   - Create migration: `alembic revision --autogenerate -m "description"`
   - Apply migration: `alembic upgrade head`

## Production Deployment

### Backend (Railway/Render/Fly.io)

1. Set environment variables:
   - `DATABASE_URL`: Production database URL
   - `BETTER_AUTH_SECRET`: Strong secret key
   - `ALLOWED_ORIGINS`: Production frontend URL
   - `ENVIRONMENT=production`

2. Deploy command:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Frontend (Vercel)

1. Connect GitHub repository to Vercel
2. Set environment variables:
   - `NEXT_PUBLIC_BACKEND_URL`: Production backend URL
   - `DATABASE_URL`: Production database URL

3. Deploy automatically on push to main branch

## Next Steps

- [ ] Customize the UI colors in `frontend/tailwind.config.ts`
- [ ] Add more task fields (priority, due date, tags)
- [ ] Implement task search and filtering
- [ ] Add task categories/projects
- [ ] Enable social authentication (Google, GitHub)
- [ ] Deploy to production

## Support

- **Backend README**: `backend/README.md`
- **Frontend README**: `frontend/README.md`
- **API Docs**: http://localhost:8000/docs (when running)
- **Issues**: Report bugs on GitHub

## Features Checklist

- [x] User authentication (signup/signin)
- [x] JWT-based authorization
- [x] Create tasks
- [x] View tasks (with filtering)
- [x] Edit tasks
- [x] Toggle task completion
- [x] Delete tasks
- [x] User isolation
- [x] Responsive design
- [x] Form validation
- [x] Error handling
- [x] Loading states

Congratulations! You now have a fully functional todo application running locally! 🎉
