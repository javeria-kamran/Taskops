# Todo App - Hackathon II
 
## Project Overview
This is a monorepo using GitHub Spec-Kit for spec-driven development.
 
## Spec-Kit Structure
Specifications are organized in /specs:
- /specs/overview.md - Project overview
- /specs/features/ - Feature specs (what to build)
- /specs/api/ - API endpoint and MCP tool specs
- /specs/database/ - Schema and model specs
- /specs/ui/ - Component and page specs
 
## How to Use Specs
1. Always read relevant spec before implementing
2. Reference specs with: @specs/features/task-crud.md
3. Update specs if requirements change
 
## Project Structure
- /frontend - Next.js 14 app
- /backend - Python FastAPI server
 
## Development Workflow
1. Read spec: @specs/features/[feature].md
2. Implement backend: @backend/CLAUDE.md
3. Implement frontend: @frontend/CLAUDE.md
4. Test and iterate
 
## Commands
- Frontend: cd frontend && npm run dev
- Backend: cd backend && uvicorn main:app --reload
- Both: docker-compose up

## Active Technologies
- Python 3.13+ + UV (package manager), pytest (testing framework), standard Python libraries only (001-phase1-console-app)
- In-memory data structures (no external database or file persistence) (001-phase1-console-app)

## Recent Changes
- 001-phase1-console-app: Added Python 3.13+ + UV (package manager), pytest (testing framework), standard Python libraries only
