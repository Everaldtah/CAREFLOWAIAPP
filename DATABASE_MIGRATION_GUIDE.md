# Database Migration Guide for CareFlow AI

## PostgreSQL Database Setup on Railway

This guide explains how to set up and migrate the PostgreSQL database for CareFlow AI deployment.

---

## Database Schema Overview

CareFlow AI uses the following main tables:

| Table | Description |
|-------|-------------|
| `tenants` | Multi-tenant organizations |
| `clinics` | Medical clinics/practices |
| `users` | User accounts (clinicians, staff, patients) |
| `patients` | Patient records and PHI |
| `appointments` | Scheduled appointments |
| `encounters` | Patient encounters/visits |
| `clinical_notes` | Medical documentation |
| `triage_assessments` | AI triage results |
| `messages` | Secure messaging |
| `documents` | Document storage |

---

## Step 1: Create PostgreSQL Database in Railway

1. Go to your Railway project
2. Click **New Service** → **Database** → **PostgreSQL**
3. Railway will create a PostgreSQL 15 database with `pgvector` extension

---

## Step 2: Get Database Connection String

In Railway dashboard:
1. Click on your PostgreSQL service
2. Go to **Variables** tab
3. Copy `DATABASE_URL` (format: `postgresql://user:password@host:port/dbname`)

---

## Step 3: Set Backend Database URL

In Railway backend service:
1. Add environment variable `DATABASE_URL` with value: `${{Postgres.DATABASE_URL}}`
2. This automatically links the backend to the PostgreSQL service

---

## Step 4: Run Alembic Migrations

### Option A: Via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Select your project
railway project

# Open shell in backend service
railway run bash

# Inside the shell, run migrations
cd /app
alembic upgrade head

# Exit shell
exit
```

### Option B: Via Local Machine

```bash
# Copy DATABASE_URL from Railway
export DATABASE_URL="postgresql://user:password@host:port/dbname"

cd C:/Users/evera/careflow-ai/backend

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies if needed
pip install alembic sqlalchemy psycopg2-binary

# Run migrations
alembic upgrade head
```

### Option C: Via Railway Dashboard (Temporary)

1. Go to backend service in Railway
2. Click **Deployments** tab
3. Click **New Deployment** → **Add Command**
4. Add command: `alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## Step 5: Verify Database Migration

```bash
# Run health check
curl https://api.careflowai.veraldlabs.co.uk/health

# Should return: {"status":"healthy","database":"connected"}
```

---

## Migration Files

The database schema is defined in Alembic migrations:

```
backend/alembic/versions/
├── 001_initial_schema.py          # Core tables (tenants, users, patients)
├── 002_encounters_and_notes.py    # Clinical encounters and notes
├── 003_ai_features.py             # AI triage and scribe features
└── ...
```

---

## Creating a New Migration

If you modify the database schema:

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Description of changes"

# Review the migration file
alembic upgrade head

# Test locally first!
```

---

## Rolling Back Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# See migration history
alembic history
```

---

## pgvector Extension

CareFlow AI uses `pgvector` for AI embeddings (semantic search):

```sql
-- Enable extension (already done by Railway)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create vector column for embeddings
ALTER TABLE documents ADD COLUMN embedding vector(1536);

-- Create vector index for similarity search
CREATE INDEX documents_embedding_idx ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

---

## Database Backup

### Automatic Backups (Railway)

Railway automatically backs up PostgreSQL databases daily.

### Manual Backup

```bash
# Via pg_dump
pg_dump $DATABASE_URL > careflow_backup.sql

# Via Railway CLI
railway run "pg_dump $DATABASE_URL" > backup.sql
```

### Restore from Backup

```bash
psql $DATABASE_URL < careflow_backup.sql
```

---

## Troubleshooting

### Migration Fails

1. Check DATABASE_URL is correct
2. Verify PostgreSQL service is running
3. Check migration logs in Railway

```bash
# Check current migration version
railway run "alembic current"

# Check migration status
railway run "alembic show"
```

### Permission Denied

1. Verify DATABASE_URL has correct permissions
2. Railway automatically grants proper permissions

### Connection Timeout

1. Check PostgreSQL service is running
2. Verify DATABASE_URL format is correct
3. Check Railway service networking

---

## Seeding Initial Data

To create an initial admin user and sample data:

```bash
# Create admin user script
railway run "python -c 'from app.core.seed import create_admin_user; create_admin_user()'"
```

Or via the frontend registration after deployment.

---

## Production Checklist

- [x] PostgreSQL service created in Railway
- [x] DATABASE_URL configured in backend
- [x] Alembic migrations run successfully
- [x] Database health check passing
- [x] pgvector extension enabled
- [x] Backup strategy configured

---

## Database Performance Tips

1. **Connection Pooling**: Already configured (pool_size=20)
2. **Indexes**: Automatically created by migrations
3. **Query Optimization**: Use SQLAlchemy's eager loading
4. **Monitoring**: Check Railway dashboard for slow queries

---

## Security Considerations

- All PHI is encrypted at rest (ENCRYPTION_KEY)
- Use SSL for database connections (default in Railway)
- Never commit DATABASE_URL to git
- Use read-only users for analytics queries

---

## Next Steps

After database setup:
1. Run migrations (above)
2. Create admin user via frontend
3. Test database operations
4. Monitor database performance in Railway dashboard

---

Need help? Check:
- Railway PostgreSQL docs: https://docs.railway.app/reference/postgresql
- Alembic docs: https://alembic.sqlalchemy.org/
