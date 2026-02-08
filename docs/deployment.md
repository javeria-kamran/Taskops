# Deployment Checklist & Guide

## Overview

This guide provides a comprehensive checklist for deploying the Todo Hackathon application to production. It covers pre-deployment verification, deployment steps, smoke tests, monitoring, and rollback procedures.

## Phase 11: Production Deployment & Monitoring

### Release Information
- **Release Date**: 2026-02-08
- **Version**: 1.0.0
- **Components**: Backend (FastAPI), Frontend (Next.js), Database (Neon PostgreSQL)

---

## Pre-Deployment Verification

### Environment Variables

Before deploying, verify all required environment variables are configured:

- [ ] **OPENAI_API_KEY** - Set to valid OpenAI API key (sk-...)
- [ ] **OPENAI_MODEL** - Set to gpt-4-turbo (or appropriate model)
- [ ] **DATABASE_URL** - Points to production Neon database with ssl=require
- [ ] **DATABASE_POOL_SIZE** - Set to 20 (or appropriate for traffic)
- [ ] **DATABASE_MAX_OVERFLOW** - Set to 40 (or appropriate for traffic)
- [ ] **MCP_SERVER_HOST** - Set to 0.0.0.0
- [ ] **MCP_SERVER_PORT** - Set to 5555
- [ ] **ENVIRONMENT** - Set to "production"
- [ ] **DEBUG** - Set to False
- [ ] **LOG_LEVEL** - Set to INFO or WARNING
- [ ] **LOG_FORMAT** - Set to json
- [ ] **JWT_ALGORITHM** - Set to HS256
- [ ] **JWT_EXPIRATION_HOURS** - Set to 24
- [ ] **ALLOWED_ORIGINS** - Includes frontend domain (https://app.example.com)
- [ ] **CORS_ALLOW_CREDENTIALS** - Set to true
- [ ] **CORS_ALLOW_METHODS** - Set to GET,POST,PUT,DELETE,OPTIONS
- [ ] **SENTRY_DSN** - Set to valid Sentry DSN (if using error tracking)
- [ ] **HEALTH_CHECK_INTERVAL_SECONDS** - Set to 60
- [ ] **METRICS_ENABLED** - Set to true
- [ ] **SECRET_KEY** - Strong random string (32+ chars)
- [ ] **BETTER_AUTH_SECRET** - Strong random string (32+ chars)

**Configuration File**: `.env.production` in backend directory

### Database Configuration

Ensure database is properly configured and accessible:

- [ ] **Neon Project Created** - Production database project exists in Neon
- [ ] **Database Accessible** - Test connection: `psql $DATABASE_URL -c "SELECT 1"`
- [ ] **Alembic Migrations Ready** - Latest migrations available and tested
- [ ] **Run Migrations** - Execute: `alembic upgrade head`
- [ ] **Verify Tables** - Confirm tables exist:
  - [ ] conversations
  - [ ] messages
  - [ ] tasks
  - [ ] users (if applicable)
- [ ] **Connection Pool Appropriate** - Pool size: 20-40 (based on expected load)
- [ ] **Database Backups** - Point-in-time recovery enabled in Neon
- [ ] **Read Replicas** (Optional) - Consider for high traffic scenarios

### OpenAI Configuration

Verify OpenAI API setup and quotas:

- [ ] **API Key Valid** - API key is active and has permissions
- [ ] **Quota Available** - Account has sufficient credits/quota
- [ ] **Model Available** - gpt-4-turbo is available in API key scope
- [ ] **Rate Limits Understood** - Standard: 100 requests/min (may vary by tier)
- [ ] **Domain Allowlist Configured** - Frontend domain registered in OpenAI console:
  - [ ] Production: app.example.com
  - [ ] Staging: staging.example.com (if applicable)
- [ ] **Organization ID Set** (Optional) - If using organization-level API key
- [ ] **Cost Monitoring** - Setup cost alerts in OpenAI dashboard

### Domain & CORS Configuration

Ensure domains and CORS are properly configured:

- [ ] **Frontend Domain Registered** - Domain registered with OpenAI console
- [ ] **CORS ALLOWED_ORIGINS Updated** - Matches frontend URL (https://app.example.com)
- [ ] **DNS Records Configured** - All domains pointing to correct servers
- [ ] **SSL Certificates Valid** - Certificates not expired, trusted by browsers
- [ ] **Certificate Chain Complete** - All intermediate certificates included
- [ ] **HTTPS Enforced** - All traffic redirects from HTTP to HTTPS
- [ ] **HSTS Headers** - Consider adding Strict-Transport-Security header

### Security Verification

Confirm security best practices are implemented:

- [ ] **JWT Secrets Strong** - 32+ characters, cryptographically random
- [ ] **Database Credentials Secured** - Stored in secrets manager, not in code
- [ ] **No Hardcoded Secrets** - Git grep check: `git grep -i "password\|secret\|api_key" -- "*.py" "*.ts"`
- [ ] **Environment File Permissions** - `.env.production` not in version control
- [ ] **API Key Rotation Plan** - Process documented for rotating keys
- [ ] **Rate Limiting Configured** - Protect against abuse
- [ ] **Input Validation** - All endpoints validate input
- [ ] **SQL Injection Prevention** - Using parameterized queries (no string interpolation)
- [ ] **CORS Properly Configured** - Only allow specific origins

### Application Configuration

Verify application settings before deployment:

- [ ] **Dependencies Installed** - Run: `pip install -r requirements.txt`
- [ ] **Frontend Dependencies** - Run: `npm install` in frontend directory
- [ ] **Environment Set to Production** - ENVIRONMENT=production in .env
- [ ] **DEBUG Flag False** - DEBUG=False to disable debug mode
- [ ] **LOG_LEVEL Appropriate** - INFO or WARNING (not DEBUG)
- [ ] **LOG_FORMAT Set to JSON** - LOG_FORMAT=json for structured logs
- [ ] **All Required Packages Updated** - Latest security patches applied
- [ ] **No Development Dependencies** - devDependencies not in production

---

## Deployment Steps

### 1. Pre-Deployment Testing

Run tests and verification before deploying:

```bash
# Test health endpoint locally
curl http://localhost:8000/health

# Run unit and integration tests
pytest tests/ -v --cov=app.chat --cov-report=html

# Run frontend tests
npm test -- --coverage

# Verify git state
git status
git log --oneline -5

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: Uncommitted changes detected"
  git diff
  exit 1
fi

# Verify no test failures
pytest tests/ -q
npm test -- --passWithNoTests

# Check logs for errors
tail -n 50 logs/app.log
```

**Expected Results**:
- [ ] All tests pass
- [ ] No uncommitted changes
- [ ] Health endpoint returns 200
- [ ] No errors in recent logs

### 2. Database Migration

Perform database migrations on production:

```bash
# Set production database URL
export DATABASE_URL="postgresql://neon_user:password@db.neon.tech/production_db?sslmode=require"

# Create backup before migration
export BACKUP_FILE="production_backup_$(date +%Y%m%d_%H%M%S).sql"
pg_dump $DATABASE_URL > $BACKUP_FILE
echo "Backup created: $BACKUP_FILE"

# Run migration
alembic upgrade head

# Verify migration success
psql $DATABASE_URL -c "\dt"  # List tables
psql $DATABASE_URL -c "SELECT COUNT(*) FROM conversations;"  # Verify data intact
```

**Expected Results**:
- [ ] Backup created successfully
- [ ] Alembic migrations completed without errors
- [ ] All tables present and accessible
- [ ] No data loss

### 3. Application Deployment

Deploy backend application:

```bash
# Build Docker image
docker build -t todo-app:1.0.0 .

# Tag as latest
docker tag todo-app:1.0.0 todo-app:latest

# Run container with production config
docker run -d \
  --env-file .env.production \
  -p 8000:8000 \
  --name todo-app-prod \
  --restart unless-stopped \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=10 \
  todo-app:1.0.0

# Verify container is running
docker ps | grep todo-app

# Check logs
docker logs todo-app-prod --tail 20
```

**Expected Results**:
- [ ] Docker image builds successfully
- [ ] Container starts and stays running
- [ ] No startup errors in logs
- [ ] Container restarts policy configured

### 4. Frontend Deployment

Deploy frontend application:

```bash
# Build Next.js application
npm run build

# Test build locally
npm run start

# Verify frontend loads on localhost:3000
curl http://localhost:3000

# Deploy to hosting platform (Vercel, Netlify, etc.)
# Example for Vercel:
npm run deploy
# Or:
vercel deploy --prod

# Verify production deployment
curl https://app.example.com
```

**Expected Results**:
- [ ] Build completes without errors
- [ ] Local test successful
- [ ] Production URL accessible
- [ ] HTTPS working correctly

### 5. Smoke Tests

Run smoke tests to verify core functionality:

```bash
# Test 1: Access frontend
curl https://app.example.com
# Expected: 200 OK, HTML content

# Test 2: Health endpoint
curl https://api.example.com/health
# Expected: 200 OK, JSON response with status="healthy"

# Test 3: Create task via API (requires auth token)
curl -X POST https://api.example.com/api/{user_id}/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "create task: test task"}'
# Expected: 200 OK, task created

# Test 4: Retrieve tasks
curl https://api.example.com/api/{user_id}/conversations \
  -H "Authorization: Bearer <token>"
# Expected: 200 OK, conversation list

# Test 5: Database connectivity
psql $DATABASE_URL -c "SELECT COUNT(*) FROM conversations;"
# Expected: Returns row count
```

**Smoke Test Checklist**:
- [ ] User can access frontend without errors
- [ ] Frontend loads styles and JavaScript correctly
- [ ] Health endpoint returns 200 with correct status
- [ ] User can authenticate with valid credentials
- [ ] User can create new task via chat interface
- [ ] Task appears in database immediately
- [ ] Can list pending tasks
- [ ] Conversation persists across browser sessions
- [ ] Error handling works (invalid input rejected with 400)
- [ ] JWT authentication enforced (missing token returns 401)
- [ ] CORS headers present in response
- [ ] API response includes proper error messages

---

## Post-Deployment Monitoring

### Real-Time Monitoring

Monitor application health immediately after deployment:

```bash
# Monitor health endpoint (every 10 seconds)
watch -n 10 'curl -s https://api.example.com/health | jq'

# Monitor application logs (streaming)
docker logs -f todo-app-prod

# Monitor database connections
psql $DATABASE_URL -c "\copy (SELECT count(*) as active_connections FROM pg_stat_activity) to stdout"

# Monitor system resources
docker stats todo-app-prod
```

**Critical Metrics to Monitor**:
- [ ] Health endpoint returns 200 (database_connected: true)
- [ ] Error logs remain below threshold
- [ ] Database connections < 20 (pool size)
- [ ] CPU usage < 80%
- [ ] Memory usage < 80%
- [ ] No restart loops in container

### Performance Metrics

Track key performance indicators:

```
Response Times (Target):
- Health endpoint: < 10ms (database latency < 5ms)
- Chat endpoint: < 5 seconds average
- Task creation: < 2 seconds average
- List tasks: < 1 second average

Error Rates (Target):
- API error rate: < 0.1%
- Database connection errors: 0
- Authentication failures: < 1% of requests

Resource Usage (Target):
- Database connections: < 20 (pool size)
- Memory: < 500MB
- CPU: < 50%

Uptime (Target):
- Application: 99.9% uptime
```

### Alert Configuration

Setup alerts for critical issues:

1. **Health Endpoint Alerts**
   - [ ] Alert if `/health` returns 503 for > 5 minutes
   - [ ] Action: Page on-call engineer, check logs

2. **Error Rate Alerts**
   - [ ] Alert if error rate > 1% for > 10 minutes
   - [ ] Action: Check logs for common errors, assess severity

3. **Database Connection Pool Alerts**
   - [ ] Alert if connections > 15 (75% of pool size)
   - [ ] Action: Monitor scaling, may need to increase pool size

4. **OpenAI API Rate Limit Alerts**
   - [ ] Alert if approaching 100 requests/minute
   - [ ] Action: Implement request queuing if needed

5. **Disk Space Alerts**
   - [ ] Alert if disk usage > 80%
   - [ ] Action: Review log rotation, clean up old logs

6. **Memory/CPU Alerts**
   - [ ] Alert if memory usage > 80% or CPU > 80%
   - [ ] Action: Assess need for scaling resources

### Monitoring Tools

Consider implementing monitoring with:

- **Sentry** - Error tracking and performance monitoring
- **Prometheus** - Metrics collection
- **Grafana** - Visualization and dashboards
- **ELK Stack** - Centralized logging
- **DataDog** - Full-stack monitoring

**Sentry Setup Example**:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT")
)
```

---

## Scaling Considerations

### Horizontal Scaling

The application is designed to be stateless and horizontally scalable:

```bash
# Run multiple instances behind load balancer
docker run -d --env-file .env.production -p 8001:8000 --name todo-app-prod-1 todo-app:1.0.0
docker run -d --env-file .env.production -p 8002:8000 --name todo-app-prod-2 todo-app:1.0.0
docker run -d --env-file .env.production -p 8003:8000 --name todo-app-prod-3 todo-app:1.0.0

# Use nginx or similar for load balancing across instances
```

**Scaling Checklist**:
- [ ] Application is stateless (no local session storage)
- [ ] Database connection pooling configured
- [ ] Load balancer distributes requests evenly
- [ ] Health checks configured on load balancer
- [ ] Each instance has unique logs
- [ ] Monitoring aggregates metrics across instances

### Database Scaling

Optimize database performance for production:

```sql
-- Create indexes on frequently queried columns
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Analyze tables for query planner optimization
ANALYZE conversations;
ANALYZE messages;
ANALYZE tasks;
```

**Database Scaling Checklist**:
- [ ] Indexes created on foreign key columns
- [ ] Query statistics updated (ANALYZE)
- [ ] Connection pool configured (20-40)
- [ ] Connection timeout appropriate (30 seconds)
- [ ] Read replicas considered for high traffic
- [ ] Backup and recovery tested

### Performance Optimization

Monitor and optimize for production performance:

```bash
# Monitor slow queries (if pg_stat_statements enabled)
psql $DATABASE_URL -c "
SELECT query, mean_time, calls FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 10;"

# Monitor connections
psql $DATABASE_URL -c "
SELECT usename, application_name, count(*) FROM pg_stat_activity
GROUP BY usename, application_name;"
```

---

## Rollback Plan

If deployment fails or critical issues arise:

### Immediate Rollback

```bash
# 1. Stop current deployment
docker stop todo-app-prod
docker rm todo-app-prod

# 2. Restore previous version
docker run -d \
  --env-file .env.production \
  -p 8000:8000 \
  --name todo-app-prod \
  --restart unless-stopped \
  todo-app:previous-version

# 3. Verify rollback successful
curl -s https://api.example.com/health | jq
```

### Database Rollback

```bash
# 1. Rollback last migration (if applicable)
alembic downgrade -1

# 2. Restore from backup (if data corrupted)
psql $DATABASE_URL < $BACKUP_FILE

# 3. Verify data integrity
psql $DATABASE_URL -c "
SELECT table_name FROM information_schema.tables
WHERE table_schema='public';"
```

### Frontend Rollback

```bash
# 1. Rollback frontend to previous deployment
vercel deploy --prod --env production -- @previous-deployment-id

# 2. Or clear cache and rebuild
npm run build
npm run deploy
```

### Post-Rollback Investigation

After rollback:

1. [ ] Analyze error logs thoroughly
2. [ ] Identify root cause
3. [ ] Create issue in tracking system
4. [ ] Fix and test locally
5. [ ] Request code review
6. [ ] Re-deploy with fix

---

## Documentation

Maintain and update documentation:

- [ ] **API Documentation** - Update /docs endpoint with health endpoint
- [ ] **Environment Variables** - Document all required and optional vars
- [ ] **Troubleshooting Guide** - Common issues and solutions
- [ ] **Monitoring Setup** - How to access monitoring tools
- [ ] **On-Call Runbook** - Playbook for on-call engineers
- [ ] **Architecture Diagram** - System architecture and data flow
- [ ] **Database Schema** - Document table structure and relationships
- [ ] **Deployment Procedure** - Step-by-step deployment guide (this document)

### API Documentation Update

Update Swagger/OpenAPI documentation:

```python
# In main.py or routers
from fastapi import FastAPI
from app.routers import health_router

app = FastAPI(
    title="Todo API",
    description="Production Todo Application API",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

app.include_router(health_router.router)
```

---

## Sign-Off Checklist

Before considering deployment complete:

- [ ] All pre-deployment verification items checked
- [ ] Database migrations successful
- [ ] Application deployed and running
- [ ] Frontend deployed and accessible
- [ ] All smoke tests passed
- [ ] Monitoring configured and working
- [ ] Alerts configured and tested
- [ ] Documentation updated
- [ ] Team notified of deployment
- [ ] Status page updated (if applicable)
- [ ] Customer notification sent (if applicable)

---

## Contact & Support

For deployment issues or questions:

- **Backend Issues**: Contact backend lead
- **Frontend Issues**: Contact frontend lead
- **Database Issues**: Contact DevOps/DBA
- **OpenAI Issues**: Check OpenAI status page, contact OpenAI support
- **Monitoring Issues**: Check monitoring tool status, contact ops team

**Emergency Contacts**:
- On-Call Engineer: [contact info]
- DevOps Lead: [contact info]
- Engineering Manager: [contact info]

---

## Revision History

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 1.0.0   | 2026-02-08 | DevOps | Initial production deployment checklist |

Last Updated: 2026-02-08
