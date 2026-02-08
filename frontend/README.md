# Naz Todo - Frontend

Modern Next.js frontend for the Naz Todo application with authentication, task management, and responsive design.

## Tech Stack

- **Framework**: Next.js 16+ (App Router)
- **React**: React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with shadcn/ui patterns
- **Authentication**: Better Auth with JWT
- **State Management**: React hooks
- **Testing**: Jest with React Testing Library

## Project Structure

```
frontend/
├── app/
│   ├── (app)/                  # Protected app routes
│   │   ├── layout.tsx         # App layout with auth guard
│   │   ├── page.tsx           # Dashboard
│   │   ├── tasks/             # Task management
│   │   │   ├── page.tsx       # All tasks view
│   │   │   ├── new/           # Create task
│   │   │   └── [id]/edit/     # Edit task
│   │   └── profile/           # User profile
│   ├── (auth)/                 # Authentication routes
│   │   ├── signup/            # User registration
│   │   └── signin/            # User login
│   ├── api/                    # API routes
│   │   └── auth/[...all]/     # Better Auth handler
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Landing page
│   └── globals.css            # Global styles
├── components/
│   ├── auth/                   # Auth components
│   │   ├── auth-guard.tsx     # Route protection
│   │   ├── signup-form.tsx    # Signup form
│   │   └── signin-form.tsx    # Signin form
│   ├── tasks/                  # Task components
│   │   ├── task-form.tsx      # Create/edit task form
│   │   ├── task-item.tsx      # Task display
│   │   └── task-list.tsx      # Task list container
│   └── ui/                     # Reusable UI components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       └── dialog.tsx
├── lib/
│   ├── api.ts                  # Backend API client
│   ├── auth.ts                 # Better Auth configuration
│   └── utils.ts                # Utility functions
├── types/
│   ├── user.ts                 # User type definitions
│   └── task.ts                 # Task type definitions
├── public/
│   └── favicon.ico             # App favicon
├── .env.example               # Environment variables template
├── package.json               # Dependencies
├── tsconfig.json              # TypeScript configuration
└── tailwind.config.ts         # Tailwind configuration
```

## Setup Instructions

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running (see backend/README.md)

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` and update:
   - `NEXT_PUBLIC_BACKEND_URL`: Backend API URL (default: http://localhost:8000)
   - `DATABASE_URL`: PostgreSQL URL (for Better Auth)

4. **Start development server**
   ```bash
   npm run dev
   ```

   The app will be available at: http://localhost:3000

## Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint

# Run tests
npm test

# Run tests in watch mode
npm run test:watch
```

## Features

### Authentication
- ✅ User signup with email/password
- ✅ User signin with JWT tokens
- ✅ Protected routes with auth guard
- ✅ Automatic token refresh
- ✅ Session management

### Task Management
- ✅ Create tasks with title and description
- ✅ View all tasks with filtering (All/Active/Completed)
- ✅ Edit existing tasks
- ✅ Toggle task completion
- ✅ Delete tasks with confirmation
- ✅ Real-time UI updates

### User Experience
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Loading states for all async operations
- ✅ Error handling with user feedback
- ✅ Empty states
- ✅ Form validation
- ✅ Character count indicators
- ✅ Task statistics

## Pages

### Public Routes
- `/` - Landing page with features
- `/signup` - User registration
- `/signin` - User login

### Protected Routes (Require Authentication)
- `/app` - Dashboard with quick actions
- `/app/tasks` - All tasks view with filters
- `/app/tasks/new` - Create new task
- `/app/tasks/[id]/edit` - Edit existing task
- `/app/profile` - User profile (planned)

## API Integration

The frontend communicates with the backend API using the `tasksApi` client from `lib/api.ts`:

```typescript
import { tasksApi } from "@/lib/api"

// Create task
const task = await tasksApi.create({ title: "New task", description: "..." })

// Get all tasks
const tasks = await tasksApi.getAll()

// Get completed tasks only
const completedTasks = await tasksApi.getAll(true)

// Update task
const updated = await tasksApi.update(taskId, { title: "Updated" })

// Delete task
await tasksApi.delete(taskId)

// Toggle completion
await tasksApi.toggleComplete(taskId, true)
```

## Authentication Flow

1. User signs up or signs in via auth forms
2. Backend returns JWT token and user data
3. Token stored in localStorage
4. Auth guard verifies token on protected routes
5. Token included in API requests via Authorization header



### Customizing Styles

Edit `tailwind.config.ts` to customize colors, fonts, and other design tokens.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL | http://localhost:8000 |
| `DATABASE_URL` | PostgreSQL URL for Better Auth | Required |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID (optional) | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret (optional) | - |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID (optional) | - |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth secret (optional) | - |

## Production Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Manual Deployment

```bash
# Build the application
npm run build

# Start production server
npm start
```

### Environment Configuration

For production:
- Set `NEXT_PUBLIC_BACKEND_URL` to your production API URL
- Ensure `DATABASE_URL` points to production database
- Configure OAuth credentials if using social login

## Code Quality

### Linting

```bash
npm run lint
```

### TypeScript

The project uses TypeScript strict mode for type safety:

```bash
# Type check
npx tsc --noEmit
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT
