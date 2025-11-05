# Database Migrations Guide

Complete guide for managing database migrations in development and production environments.

---

## Table of Contents

- [Overview](#overview)
- [Development Environment](#development-environment)
- [Production Environment](#production-environment)
- [Common Commands](#common-commands)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project uses **SQLAlchemy** (ORM) + **Alembic** (migrations) for database management.

### Technology Stack

- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic 1.13+
- **Database**: PostgreSQL 16
- **Driver**: psycopg2-binary

### Migration Strategy

| Environment     | Strategy  | Auto-Apply | When                        |
| --------------- | --------- | ---------- | --------------------------- |
| **Development** | Automatic | ✅ Yes     | Every Docker startup        |
| **Production**  | Manual    | ❌ No      | Via CI/CD or manual command |

---

# Development Environment

## 🛠️ Setup (First Time)

### Step 1: Start Docker

```bash
docker-compose --profile dev up --build
```

**What happens:**

1. PostgreSQL container starts on port `5432`
2. `bankparser-dev` container starts on port `8001`
3. Waits for PostgreSQL health check ✅
4. Runs `docker-entrypoint.sh`:
   - Waits for database connection
   - Executes: `alembic upgrade head`
   - Applies any pending migrations
5. FastAPI app starts

**First time:** No migrations exist yet, so no tables are created.

---

### Step 2: Generate Initial Migration

**Command:**

```bash
docker exec -it bankparser-dev alembic revision --autogenerate -m "Initial migration"
```

**What this does:**

- Connects to the empty database
- Reads your SQLAlchemy models from `app/core/db/models.py`
- Compares models with current database state (empty)
- Generates migration file in `alembic/versions/`

**Output:**

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.autogenerate.compare] Detected added table 'projects'
INFO  [alembic.autogenerate.compare] Detected added table 'categories'
INFO  [alembic.autogenerate.compare] Detected added table 'bank_accounts'
...
Generating /app/alembic/versions/20251104_1234_initial_migration.py ... done
```

**File created:** `alembic/versions/20251104_1234_initial_migration.py`

---

### Step 3: Review Migration File

**Command:**

```bash
# View the generated file
cat alembic/versions/*_initial_migration.py
```

**Check for:**

- ✅ All 7 tables are created (projects, bank_accounts, categories, etc.)
- ✅ Foreign key relationships are correct
- ✅ Column types match your models
- ✅ Indexes and constraints are present

---

### Step 4: Apply Migration

**Option A: Restart Container (Automatic)**

```bash
docker-compose --profile dev restart bankparser-dev
```

**Option B: Manual Apply**

```bash
docker exec -it bankparser-dev alembic upgrade head
```

**Expected output:**

```
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, Initial migration
```

---

### Step 5: Verify Tables

**Via psql:**

```bash
docker exec -it bankparser-postgres psql -U postgres -d bankparser -c "\dt"
```

**Expected output:**

```
                      List of relations
 Schema |              Name               | Type  |  Owner
--------+---------------------------------+-------+----------
 public | alembic_version                 | table | postgres
 public | bank_accounts                   | table | postgres
 public | bank_statement_entries          | table | postgres
 public | bank_statement_entry_splits     | table | postgres
 public | bank_statement_files            | table | postgres
 public | categories                      | table | postgres
 public | project_category_positions      | table | postgres
 public | projects                        | table | postgres
(8 rows)
```

**Via pgAdmin:**

1. Connect to `localhost:5432`
2. Database: `bankparser`
3. Schemas → public → Tables
4. Should see all 7 tables + `alembic_version`

---

## 🔄 Making Changes to Models

### Workflow

**1. Modify SQLAlchemy Models**

Example: Add a new column to `Project` model

```python
# app/core/db/models.py
class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    # ... existing fields ...

    # NEW FIELD
    project_code = Column(String(50), nullable=True)  # ← Add this
```

**2. Generate Migration**

```bash
docker exec -it bankparser-dev alembic revision --autogenerate -m "Add project_code to projects"
```

**3. Review Generated File**

```bash
# Find the newest migration
ls -lt alembic/versions/ | head -2

# Review it
cat alembic/versions/20251104_5678_add_project_code_to_projects.py
```

**Should contain:**

```python
def upgrade():
    op.add_column('projects', sa.Column('project_code', sa.String(length=50), nullable=True))

def downgrade():
    op.drop_column('projects', 'project_code')
```

**4. Apply Migration**

```bash
# Automatic (restart)
docker-compose --profile dev restart bankparser-dev

# OR Manual
docker exec -it bankparser-dev alembic upgrade head
```

**5. Verify Change**

```bash
# Check column was added
docker exec -it bankparser-postgres psql -U postgres -d bankparser -c "\d projects"
```

---

## 🔍 Development Commands

### Check Current Migration Version

```bash
docker exec -it bankparser-dev alembic current
```

### View Migration History

```bash
docker exec -it bankparser-dev alembic history
```

### View Pending Migrations

```bash
docker exec -it bankparser-dev alembic history --verbose
```

### Rollback Last Migration

```bash
docker exec -it bankparser-dev alembic downgrade -1
```

### Rollback to Specific Version

```bash
docker exec -it bankparser-dev alembic downgrade <revision_id>
```

### Create Empty Migration (for manual SQL)

```bash
docker exec -it bankparser-dev alembic revision -m "custom changes"
```

---

## 🚫 What NOT to Do in Development

❌ **Don't manually edit the database** - Always use migrations
❌ **Don't skip reviewing generated migrations** - Auto-generate can miss things
❌ **Don't commit migrations without testing** - Test locally first
❌ **Don't delete migration files** - This breaks the migration chain

---

## 🧹 Reset Database (Development Only!)

**Warning:** This deletes all data!

```bash
# Option 1: Drop and recreate database
docker exec -it bankparser-postgres psql -U postgres -c "DROP DATABASE bankparser;"
docker exec -it bankparser-postgres psql -U postgres -c "CREATE DATABASE bankparser;"
docker-compose --profile dev restart bankparser-dev

# Option 2: Drop all tables via SQLAlchemy
docker exec -it bankparser-dev python -c "
from app.core.db.base import Base
from app.core.db.session import engine
Base.metadata.drop_all(engine)
"
docker exec -it bankparser-dev alembic upgrade head

# Option 3: Nuclear option - delete volume
docker-compose --profile dev down -v
docker-compose --profile dev up --build
# Then generate and apply migrations again
```

---

# Production Environment

## ⚠️ Important Production Rules

🚨 **NEVER run auto-migrations in production**
✅ **Always test on staging first**
✅ **Always backup database before migrations**
✅ **Always have rollback plan ready**
✅ **Run migrations during maintenance windows**
✅ **Use CI/CD pipeline for consistency**

---

## 🏗️ Production Setup

### Prerequisites

1. **Production Database** (Not in Docker)
   - Azure Database for PostgreSQL
   - AWS RDS PostgreSQL
   - Google Cloud SQL
   - Self-hosted PostgreSQL

2. **Application Server**
   - Docker container
   - Azure App Service
   - Kubernetes cluster
   - VM with Python environment

3. **CI/CD Pipeline** (Recommended)
   - GitHub Actions
   - GitLab CI
   - Azure DevOps
   - Jenkins

---

## 📋 Production Migration Workflow

### Step 1: Develop and Test Migration

**On dev environment:**

```bash
# 1. Make model changes
# 2. Generate migration
docker exec -it bankparser-dev alembic revision --autogenerate -m "Description"

# 3. Review migration file
cat alembic/versions/20251104_xxxx_description.py

# 4. Test migration
docker exec -it bankparser-dev alembic upgrade head

# 5. Test rollback
docker exec -it bankparser-dev alembic downgrade -1

# 6. Re-apply
docker exec -it bankparser-dev alembic upgrade head

# 7. Test application functionality
curl http://localhost:8001/health
```

---

### Step 2: Code Review

**Before merging to main:**

1. ✅ Review migration file in PR
2. ✅ Ensure `upgrade()` and `downgrade()` are correct
3. ✅ Check for data loss risks
4. ✅ Verify foreign key constraints
5. ✅ Ensure backward compatibility if needed

---

### Step 3: Deploy to Staging

**Test on staging environment first!**

```bash
# SSH to staging server or use CI/CD

# Set staging environment variables
export POSTGRES_HOST=staging-db.azure.com
export POSTGRES_USER=staginguser
export POSTGRES_PASSWORD=xxxxx
export POSTGRES_DB=bankparser_staging
export POSTGRES_PORT=5432

# Backup database
pg_dump -h staging-db.azure.com -U staginguser bankparser_staging > backup_$(date +%Y%m%d).sql

# Run migrations
alembic upgrade head

# Verify
alembic current

# Test application
# Run integration tests
# Verify functionality
```

---

### Step 4: Deploy to Production

**Option 1: Via CI/CD Pipeline (Recommended)**

**GitHub Actions Example:**

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run Database Migrations
        run: |
          alembic upgrade head
        env:
          POSTGRES_HOST: ${{ secrets.PROD_DB_HOST }}
          POSTGRES_USER: ${{ secrets.PROD_DB_USER }}
          POSTGRES_PASSWORD: ${{ secrets.PROD_DB_PASSWORD }}
          POSTGRES_DB: ${{ secrets.PROD_DB_NAME }}
          POSTGRES_PORT: 5432

      - name: Verify Migration
        run: |
          alembic current

  deploy:
    needs: migrate
    runs-on: ubuntu-latest
    steps:
      # Deploy application after migrations succeed
      - name: Deploy to Azure/AWS/etc
        run: |
          # Your deployment commands
```

---

**Option 2: Manual Execution via SSH**

```bash
# 1. SSH to production server
ssh user@production-server.com

# 2. Navigate to application directory
cd /var/www/bankparser

# 3. Pull latest code (includes migration files)
git pull origin main

# 4. Activate virtual environment (if not using Docker)
source venv/bin/activate

# 5. Install any new dependencies
pip install -r requirements.txt

# 6. Backup database (CRITICAL!)
pg_dump -h prod-db.azure.com -U produser bankparser > \
  /backups/bankparser_$(date +%Y%m%d_%H%M%S).sql

# 7. Check pending migrations
alembic history --verbose

# 8. Apply migrations
alembic upgrade head

# 9. Verify migration
alembic current

# 10. Test application
curl https://api.yourapp.com/health

# 11. Monitor logs
tail -f /var/log/bankparser/app.log

# 12. If issues occur, rollback
# alembic downgrade -1
```

---

**Option 3: From Local Machine**

**⚠️ Use with caution - requires VPN/whitelist**

```bash
# 1. Create production environment file
cat > .env.production << EOF
POSTGRES_HOST=prod-db.azure.com
POSTGRES_USER=produser
POSTGRES_PASSWORD=${PROD_PASSWORD}
POSTGRES_DB=bankparser_prod
POSTGRES_PORT=5432
EOF

# 2. Backup database first!
pg_dump -h prod-db.azure.com -U produser bankparser_prod > prod_backup.sql

# 3. Load production environment
export $(cat .env.production | xargs)

# 4. Check what will be applied
alembic history --verbose

# 5. Apply migrations
alembic upgrade head

# 6. Verify
alembic current

# 7. Clean up environment file (security!)
rm .env.production
unset POSTGRES_PASSWORD
```

---

## 🔄 Production Rollback

**If migration fails or causes issues:**

### Step 1: Assess the Situation

```bash
# Check current version
alembic current

# Check logs
tail -f /var/log/app.log

# Check database state
psql -h prod-db.com -U user -d db -c "SELECT COUNT(*) FROM projects;"
```

### Step 2: Rollback Migration

```bash
# Rollback one migration
alembic downgrade -1

# Or rollback to specific version
alembic downgrade <previous_revision_id>
```

### Step 3: Restore from Backup (if needed)

```bash
# Stop application first
systemctl stop bankparser

# Restore database
psql -h prod-db.com -U user -d db < backup_20251104_143000.sql

# Stamp database with correct version
alembic stamp <revision_before_failed_migration>

# Restart application
systemctl start bankparser
```

---

## 🚫 What NOT to Do in Production

❌ **Never run auto-migrations** - No `docker-entrypoint.sh` with auto-apply
❌ **Never skip backups** - Always backup before migrations
❌ **Never test in production first** - Always test on staging
❌ **Never edit migrations after applying** - Create new migration instead
❌ **Never run migrations during peak hours** - Use maintenance windows
❌ **Never delete migration files** - Breaks migration history
❌ **Never commit database credentials** - Use secrets/environment variables

---

# Common Commands

## Quick Reference

| Task                      | Development                                                               | Production                      |
| ------------------------- | ------------------------------------------------------------------------- | ------------------------------- |
| **Generate migration**    | `docker exec -it bankparser-dev alembic revision --autogenerate -m "msg"` | Same (on staging first)         |
| **Apply migrations**      | `docker-compose restart` (auto)                                           | `alembic upgrade head` (manual) |
| **Check current version** | `docker exec -it bankparser-dev alembic current`                          | `alembic current`               |
| **View history**          | `docker exec -it bankparser-dev alembic history`                          | `alembic history`               |
| **Rollback**              | `docker exec -it bankparser-dev alembic downgrade -1`                     | `alembic downgrade -1`          |

---

# Best Practices

## Development

✅ Always review auto-generated migrations before committing
✅ Test migrations locally before pushing
✅ Use descriptive migration messages
✅ Keep migrations small and focused
✅ Test both `upgrade()` and `downgrade()`
✅ Commit migration files with code changes

## Production

✅ Always backup database before migrations
✅ Test on staging environment first
✅ Run migrations during maintenance windows
✅ Use CI/CD pipelines for consistency
✅ Monitor application after migrations
✅ Have rollback plan ready
✅ Document breaking changes
✅ Version control all migration files

## Migration Files

✅ Never edit applied migrations
✅ Never delete migration files
✅ Keep migrations in version control
✅ Use semantic names: `add_user_email`, not `migration_1`
✅ Review auto-generated migrations carefully

---

# Troubleshooting

## Common Issues

### Issue: "Can't locate revision identified by 'xyz'"

**Cause:** Migration file missing or database out of sync

**Solution:**

```bash
# Check migration files exist
ls alembic/versions/

# Stamp database with known good version
alembic stamp head

# Or stamp with specific revision
alembic stamp <revision_id>
```

---

### Issue: "Target database is not up to date"

**Cause:** Pending migrations exist

**Solution:**

```bash
# Check current version
alembic current

# Check what's pending
alembic history --verbose

# Apply pending migrations
alembic upgrade head
```

---

### Issue: "Multiple head revisions present"

**Cause:** Parallel branches in migration history

**Solution:**

```bash
# View branches
alembic branches

# Merge branches
alembic merge -m "Merge branches" <rev1> <rev2>
```

---

### Issue: "FOREIGN KEY constraint failed"

**Cause:** Data exists that violates new constraint

**Solution:**

1. Review migration to understand constraint
2. Clean/fix data before applying
3. Or modify migration to handle existing data:

```python
def upgrade():
    # Add column first (nullable)
    op.add_column('table', sa.Column('fk_id', UUID, nullable=True))

    # Migrate/fix data
    # ... custom SQL ...

    # Then add constraint
    op.alter_column('table', 'fk_id', nullable=False)
    op.create_foreign_key('fk_name', 'table', 'other_table', ['fk_id'], ['id'])
```

---

### Issue: "Connection refused" during migration

**Cause:** Database not accessible

**Solution:**

```bash
# Check database is running
docker ps | grep postgres
# or
pg_isready -h localhost -p 5432

# Check credentials
psql -h localhost -U postgres -d bankparser

# Check environment variables
echo $POSTGRES_HOST
echo $POSTGRES_USER
```

---

# File Structure

```
BankStatementParser/
├── alembic/
│   ├── versions/                           # Migration files (Git track these!)
│   │   ├── 20251104_1234_initial_migration.py
│   │   └── 20251105_5678_add_project_code.py
│   ├── env.py                              # Alembic environment config
│   ├── README                              # Quick reference
│   └── script.py.mako                      # Migration template
│
├── app/
│   └── core/
│       └── db/
│           ├── base.py                     # SQLAlchemy Base
│           ├── session.py                  # Database connection
│           └── models.py                   # SQLAlchemy models (source of truth)
│
├── docker-entrypoint.sh                    # Auto-migration script (DEV ONLY)
├── alembic.ini                             # Alembic settings
├── Dockerfile.dev                          # Dev image (with auto-migrations)
├── Dockerfile                              # Prod image (NO auto-migrations)
└── docker-compose.yml                      # Container orchestration
```

---

# Quick Start Cheat Sheet

## First Time Setup (Development)

```bash
# 1. Start containers
docker-compose --profile dev up --build

# 2. Generate initial migration
docker exec -it bankparser-dev alembic revision --autogenerate -m "Initial migration"

# 3. Apply migration
docker-compose --profile dev restart bankparser-dev

# 4. Verify
docker exec -it bankparser-postgres psql -U postgres -d bankparser -c "\dt"
```

## Making Model Changes (Development)

```bash
# 1. Edit app/core/db/models.py

# 2. Generate migration
docker exec -it bankparser-dev alembic revision --autogenerate -m "Your change description"

# 3. Review migration
cat alembic/versions/*_your_change_description.py

# 4. Apply (auto on restart)
docker-compose --profile dev restart bankparser-dev
```

## Production Deployment

```bash
# 1. Test on staging first!

# 2. Backup production database
pg_dump -h prod-db.com -U user db > backup.sql

# 3. Apply migrations
alembic upgrade head

# 4. Verify
alembic current
```

---

**Need help?** Check the [Troubleshooting](#troubleshooting) section or contact the team.
