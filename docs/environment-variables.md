# Environment Variables & Configuration Guide

This guide explains where to store every variable in development, Docker, and production.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│ Configuration Flow                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Local Dev (.env)  →  Docker (.env)  →  Production (Secrets)      │
│                                                                     │
│  .env              .env                 K8s Secrets                │
│  (gitignored)      (gitignored)         AWS Secrets Manager        │
│                                         Google Secret Manager      │
│                                         Azure Key Vault            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Local Development (Python)

### Location: `apps/backend/.env`

**Status:** Gitignored (never committed)

**Setup:**
```bash
cp apps/backend/.env.example apps/backend/.env
nano apps/backend/.env  # Add your secrets
```

**File Contents:**
```bash
# Application
APP_NAME=cpq-hvac
APP_ENV=local                    # Options: local, dev, staging, production
APP_DEBUG=false                  # true only for debugging (exposes stack traces)
APP_HOST=0.0.0.0
APP_PORT=8000

# Database (local PostgreSQL)
DATABASE_URL=postgresql+psycopg://cpq:your-local-password@localhost:5432/cpq_hvac

# Logging
LOG_LEVEL=INFO                   # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# CORS (browser cross-origin)
CORS_ORIGINS=http://localhost:3000,http://localhost:3012

# OpenAI API (required for agent feature)
OPENAI_API_KEY=sk-proj-your-actual-key-here
OPENAI_MODEL=gpt-4-mini

# Tracing (optional)
OTEL_ENABLED=false
```

**Key Points:**
- ✅ Keep `.env` in `.gitignore`
- ✅ Use `localhost` for DB (local development)
- ✅ `APP_DEBUG=false` by default (prevents stack trace exposure)
- ❌ Never commit this file
- ❌ Never check in with real API keys

**How Pydantic Loads It:**
```python
# apps/backend/app/core/config.py
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",        # ← Loads from here
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    # ... other fields
```

---

## 2. Docker Compose (Container Orchestration)

### Location: `.env` in project root (next to `docker-compose.yml`)

**Status:** Gitignored (never committed)

**Setup:**
```bash
cp .env.example .env
nano .env  # Add your secrets
docker compose up -d
```

**File Contents:**
```bash
# Database
DB_USER=cpq
DB_PASSWORD=your-strong-password-here          # ⚠️ Change this
DB_NAME=cpq_hvac
DB_PORT=5432

# API
API_PORT=8000
APP_ENV=local
APP_DEBUG=false

# Frontend
FRONTEND_PORT=3000

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3012

# Secrets
OPENAI_API_KEY=sk-proj-your-api-key-here
```

**How Docker Compose Uses It:**
```yaml
# docker-compose.yml
services:
  db:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}  # ← Reads from .env
      POSTGRES_USER: ${DB_USER:-cpq}
      POSTGRES_DB: ${DB_NAME:-cpq_hvac}

  api:
    environment:
      DATABASE_URL: postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      # etc.
```

**Key Points:**
- ✅ Variables injected into containers from `.env`
- ✅ DB hostname is `db` (Docker internal DNS)
- ❌ Never hardcode values directly in compose file
- ❌ Never commit `.env` with real secrets

---

## 3. Production Deployments

### Option A: Kubernetes (Recommended)

**Location:** `Secret` objects (stored in etcd)

**Setup:**
```bash
# Create secret from file
kubectl create secret generic cpq-secrets \
  --from-literal=OPENAI_API_KEY=sk-proj-... \
  --from-literal=DB_PASSWORD=... \
  --from-literal=DATABASE_URL=postgresql+psycopg://... \
  -n production

# Or from file
kubectl create secret generic cpq-secrets \
  --from-file=.env \
  -n production
```

**YAML Reference:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cpq-secrets
  namespace: production
type: Opaque
stringData:
  OPENAI_API_KEY: sk-proj-production-key
  DATABASE_URL: postgresql+psycopg://user:pwd@prod-db-host/cpq_hvac
  POSTGRES_PASSWORD: secure-password
  APP_ENV: production
  APP_DEBUG: "false"
  CORS_ORIGINS: https://yourdomain.com
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cpq-api
spec:
  containers:
  - name: api
    image: cpq-api:latest
    envFrom:
    - secretRef:
        name: cpq-secrets  # ← Injects all variables
    ports:
    - containerPort: 8000
```

### Option B: AWS

**Location:** AWS Secrets Manager or Parameter Store

**Setup - Secrets Manager:**
```bash
# Create secret
aws secretsmanager create-secret \
  --name cpq-api-secrets \
  --secret-string '{
    "OPENAI_API_KEY": "sk-proj-...",
    "DATABASE_URL": "postgresql+psycopg://...",
    "DB_PASSWORD": "..."
  }' \
  --region us-east-1

# Retrieve in Lambda/ECS
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='cpq-api-secrets')
secrets = json.loads(secret['SecretString'])
```

**Setup - Parameter Store (simpler):**
```bash
# Store each variable
aws ssm put-parameter \
  --name /cpq/api/OPENAI_API_KEY \
  --value "sk-proj-..." \
  --type SecureString

aws ssm put-parameter \
  --name /cpq/api/DATABASE_URL \
  --value "postgresql+psycopg://..." \
  --type SecureString

# Retrieve
import boto3
ssm = boto3.client('ssm')
key = ssm.get_parameter(Name='/cpq/api/OPENAI_API_KEY', WithDecryption=True)
print(key['Parameter']['Value'])
```

### Option C: Google Cloud

**Location:** Google Secret Manager

```bash
# Create secret
echo -n "sk-proj-..." | gcloud secrets create cpq-openai-key \
  --replication-policy="automatic"

# Create secret with JSON
gcloud secrets create cpq-api-config --data-file=secrets.json

# Use in Cloud Run
gcloud run deploy cpq-api \
  --set-env-vars OPENAI_API_KEY=projects/12345/secrets/cpq-openai-key/versions/latest
```

### Option D: Azure

**Location:** Azure Key Vault

```bash
# Create vault
az keyvault create --name cpq-vault --resource-group mygroup

# Store secret
az keyvault secret set --vault-name cpq-vault \
  --name OPENAI-API-KEY \
  --value "sk-proj-..."

# Use in Azure Container Instances
az container create \
  --name cpq-api \
  --environment-variables OPENAI_API_KEY=sk-proj-...
```

### Option E: Heroku / Vercel / Netlify

**Location:** Platform Configuration UI

**Heroku:**
```bash
# Set environment variables
heroku config:set OPENAI_API_KEY=sk-proj-...
heroku config:set DATABASE_URL=postgresql+psycopg://...

# View all
heroku config
```

**Vercel:**
1. Go to Project Settings → Environment Variables
2. Add variables with scopes (Production, Preview, Development)
3. Redeploy to apply

**Netlify:**
1. Site Settings → Build & Deploy → Environment
2. Add environment variables
3. Redeploy

---

## 4. CI/CD Pipelines

### GitHub Actions

**Location:** Repository Settings → Secrets and Variables

```yaml
# .github/workflows/deploy.yml
name: Deploy
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy API
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          DOCKER_TOKEN: ${{ secrets.DOCKER_TOKEN }}
        run: |
          docker login -u ${{ secrets.DOCKER_USER }} -p $DOCKER_TOKEN
          docker build -t cpq-api:${{ github.sha }} .
          docker push cpq-api:${{ github.sha }}
          # Deploy...
```

### GitLab CI

**Location:** Project Settings → CI/CD → Variables

```yaml
# .gitlab-ci.yml
stages:
  - deploy

deploy_api:
  stage: deploy
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD
    - docker build -t $CI_REGISTRY_IMAGE:latest .
    - docker push $CI_REGISTRY_IMAGE:latest
  environment:
    name: production
  only:
    - main
```

---

## Complete Variable Reference

| Variable | Dev | Docker | Production | Type | Example |
|----------|-----|--------|------------|------|---------|
| `APP_NAME` | ✅ | ✅ | ✅ | String | `cpq-hvac` |
| `APP_ENV` | ✅ | ✅ | ✅ | String | `local`, `production` |
| `APP_DEBUG` | ✅ | ✅ | ✅ | Boolean | `false` |
| `DATABASE_URL` | ✅ | ✅ | ✅ | URL | `postgresql+psycopg://...` |
| `OPENAI_API_KEY` | ✅ | ✅ | ✅ | Secret | `sk-proj-...` |
| `CORS_ORIGINS` | ✅ | ✅ | ✅ | List | `http://localhost:3000` |
| `LOG_LEVEL` | ✅ | ✅ | ✅ | String | `INFO`, `DEBUG`, `WARNING` |
| `OTEL_ENABLED` | ✅ | ✅ | ❌ | Boolean | `false` |
| `DB_USER` | ❌ | ✅ | ❌ | String | `cpq` |
| `DB_PASSWORD` | ❌ | ✅ | ❌ | Secret | (Docker only) |
| `DB_NAME` | ❌ | ✅ | ❌ | String | `cpq_hvac` |

---

## Environment-Specific Examples

### Local Development
```bash
# apps/backend/.env
DATABASE_URL=postgresql+psycopg://cpq:local-pwd@localhost:5432/cpq_hvac
APP_ENV=local
APP_DEBUG=false
OPENAI_API_KEY=sk-proj-dev-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:3012
```

### Staging
```bash
# Set via CI/CD or platform UI
DATABASE_URL=postgresql+psycopg://cpq:staging-pwd@staging-db.example.com/cpq_hvac
APP_ENV=staging
APP_DEBUG=false
OPENAI_API_KEY=sk-proj-staging-key-here
CORS_ORIGINS=https://staging.yourdomain.com
```

### Production
```bash
# Set via secrets manager (not in code)
DATABASE_URL=postgresql+psycopg://cpq:prod-pwd@prod-db.example.com/cpq_hvac
APP_ENV=production
APP_DEBUG=false
OPENAI_API_KEY=sk-proj-production-key-here
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
LOG_LEVEL=WARNING
```

---

## Security Best Practices

✅ **DO:**
- Store secrets in platform-native secret managers
- Use different secrets per environment
- Rotate secrets quarterly
- Enable secret scanning (GitHub)
- Audit secret access logs
- Use read-only DB credentials where possible
- Encrypt secrets in transit (HTTPS/TLS)

❌ **DON'T:**
- Commit `.env` files
- Hardcode secrets in code
- Log sensitive values
- Share secrets via email/chat
- Use weak passwords (< 32 chars)
- Reuse secrets across environments
- Store secrets in comments
- Print secrets in debug output

---

## Troubleshooting

### "Module not found: OPENAI_API_KEY"
```python
# Check in Python:
from app.core.config import get_settings
settings = get_settings()
print(settings.openai_api_key)  # Should print your key
```

### "Connection refused: localhost:5432"
```bash
# For local dev, ensure PostgreSQL is running:
psql -U cpq -d cpq_hvac -c "SELECT 1"

# For Docker, ensure db service is up:
docker compose ps db
```

### "CORS error in browser console"
```bash
# Check CORS_ORIGINS environment variable:
echo $CORS_ORIGINS

# Should include your frontend origin:
# http://localhost:3000 (for local dev)
```

### "403 Unauthorized on OpenAI API"
```bash
# Verify API key is set correctly:
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models | head
```

---

## References

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [12 Factor App: Config](https://12factor.net/config)
- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
