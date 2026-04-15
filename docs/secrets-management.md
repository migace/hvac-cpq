# Secrets & Environment Variables Management

This guide explains how to properly handle sensitive configuration (API keys, database credentials, etc.) in development and production environments.

## Overview

**Never commit secrets to git.** This codebase uses `.env` files for local development and environment-based configuration for containerized/production deployments.

---

## Development (Local)

### Setup

1. **Copy `.env.example` to `.env`:**
   ```bash
   cp apps/backend/.env.example apps/backend/.env
   ```

2. **Add your secrets to `.env`:**
   ```bash
   # apps/backend/.env (NOT committed to git)
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   DATABASE_URL=postgresql+psycopg://cpq:secure-password@localhost:5432/cpq_hvac
   ```

3. **Verify `.env` is in `.gitignore`:**
   ```bash
   cat .gitignore | grep -i env
   # Should show: apps/backend/.env, .env, etc.
   ```

4. **Run locally:**
   ```bash
   cd apps/backend
   source .venv/bin/activate
   python -m uvicorn app.main:app --reload
   ```

### Important Rules for Development

✅ **DO:**
- Keep `.env` in `.gitignore`
- Store all API keys in `.env` (never in code)
- Use different API keys per environment
- Rotate keys periodically

❌ **DON'T:**
- Commit `.env` to git
- Share `.env` files via email or chat
- Use the same key across environments
- Hardcode secrets in `docker-compose.yml`

---

## Docker Compose (Local Containers)

### Configuration

**`docker-compose.yml`** uses environment variable substitution:

```yaml
api:
  environment:
    DATABASE_URL: postgresql+psycopg://${DB_USER:-cpq}:${DB_PASSWORD:-changeme}@db:5432/${DB_NAME:-cpq_hvac}
    OPENAI_API_KEY: ${OPENAI_API_KEY:-}  # Pulled from host .env
```

### Running with Docker Compose

```bash
# Create .env in project root (same dir as docker-compose.yml)
cat > .env << EOF
DB_USER=cpq
DB_PASSWORD=local-dev-password
DB_NAME=cpq_hvac
OPENAI_API_KEY=sk-proj-your-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:3012
EOF

# Start containers (secrets loaded from .env)
docker compose up -d

# Verify API is running
curl http://localhost:8000/health
```

**Important:** The `.env` file in the project root is also in `.gitignore`. Don't commit it.

---

## Production Deployments

### ⚠️ Never Use `.env` Files in Production

`.env` files are only for local development. For production, use one of these approaches:

### Option 1: Environment Variables (Recommended for Most Deployments)

**Kubernetes:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cpq-api-secrets
type: Opaque
stringData:
  OPENAI_API_KEY: sk-proj-...
  DATABASE_URL: postgresql+psycopg://user:pwd@db-host/db_name
  POSTGRES_PASSWORD: secure-password-here
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cpq-api
spec:
  containers:
  - name: api
    env:
    - name: OPENAI_API_KEY
      valueFrom:
        secretKeyRef:
          name: cpq-api-secrets
          key: OPENAI_API_KEY
```

**Docker Compose (Production):**
```bash
# Use Docker secrets (not committed)
docker secret create openai_key - < /secure/path/to/key.txt

# Reference in compose file
services:
  api:
    environment:
      OPENAI_API_KEY: /run/secrets/openai_key
```

**Cloud Platforms:**

- **AWS:** Use AWS Secrets Manager or Parameter Store
  ```bash
  aws secretsmanager get-secret-value --secret-id cpq-api-keys
  ```

- **Google Cloud:** Use Secret Manager
  ```bash
  gcloud secrets versions access latest --secret cpq-api-key
  ```

- **Azure:** Use Key Vault
  ```bash
  az keyvault secret show --vault-name cpq-vault --name openai-key
  ```

- **Heroku / Vercel / AWS Amplify:** Platform-native secrets UI
  ```bash
  # Heroku example
  heroku config:set OPENAI_API_KEY=sk-proj-...
  ```

### Option 2: Secrets Management Services

**HashiCorp Vault:**
```python
# In app/core/config.py
from hvac import Client

vault_client = Client(url="https://vault.example.com")
openai_key = vault_client.secrets.kv.v2.read_secret_version(path="cpq/openai")
```

**AWS Secrets Manager:**
```python
import boto3

def get_secrets():
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId="cpq-api-keys")
    return json.loads(response["SecretString"])
```

### Option 3: `.env` File in Encrypted Storage (Intermediate Approach)

If using `.env` files:
1. Encrypt the file: `gpg -c apps/backend/.env`
2. Store encrypted file in secure location (not git)
3. Decrypt at runtime: `gpg -d apps/backend/.env.gpg > /tmp/.env`
4. Load with Pydantic Settings
5. Delete decrypted file after loading

---

## Secrets by Component

### Database Credentials

**Development:**
```bash
# .env
DATABASE_URL=postgresql+psycopg://cpq:dev-password@localhost:5432/cpq_hvac
```

**Production:**
- Use VPC private database (not accessible from internet)
- Use strong passwords (32+ chars, mixed case, symbols)
- Rotate periodically
- Use read-only replicas for backups

### OpenAI API Key

**Development:**
```bash
# .env
OPENAI_API_KEY=sk-proj-your-dev-key
```

**Production:**
- Use separate API keys per environment
- Monitor usage at: https://platform.openai.com/account/usage
- Set spending limits: https://platform.openai.com/account/billing/limits
- Rotate keys quarterly

**Rotation Steps:**
```bash
# 1. Generate new key on OpenAI dashboard
# 2. Update secrets manager
aws secretsmanager update-secret --secret-id cpq-openai-key --secret-string sk-proj-new-key

# 3. Restart API service to pick up new key
# 4. Delete old key from OpenAI dashboard
```

### CORS Origins

**Development:**
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3012,http://127.0.0.1:3000
```

**Staging:**
```bash
CORS_ORIGINS=https://staging.yourdomain.com
```

**Production:**
```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## Checking for Secret Leaks

### Git History

```bash
# Search for API key patterns in git history
git log -p -S "sk-proj-" -- apps/backend/.env
git log -p -S "OPENAI_API_KEY" -- apps/backend/.env

# If secrets were committed:
# 1. Rotate the key immediately
# 2. Use BFG Repo-Cleaner to remove from history
# 3. Force-push to main (coordinate with team)
```

### Code Review

Before committing:
```bash
# Check for hardcoded secrets
grep -r "sk-proj-" apps/
grep -r "postgresql.*:.*@" apps/
grep -r "API_KEY" apps/ | grep -v ".env.example" | grep -v config.py

# These should all return only config files, not actual secrets
```

### Third-Party Scanning

Enable secret scanning on GitHub:
- Settings → Code Security & Analysis → Enable Secret Scanning
- This alerts you if secrets are accidentally pushed

---

## Checklist: Before Sending Code to Recruitment/Open Source

- [ ] No `.env` files committed (check `git status`)
- [ ] All secrets moved to `.env.example` (without actual values)
- [ ] No hardcoded API keys in code
- [ ] No passwords in `docker-compose.yml` (use `${VAR:-default}`)
- [ ] No credentials in README or documentation
- [ ] `.gitignore` includes `.env`, `*.key`, `secrets/`, etc.
- [ ] Any example credentials are obviously fake (e.g., `sk-xxx-example`)

---

## Summary Table

| Scenario | How to Store | Tool/Service |
|----------|--------------|--------------|
| **Local dev** | `.env` file (gitignored) | Pydantic Settings |
| **Docker Compose (local)** | `.env` in project root | Docker environment substitution |
| **Kubernetes** | Secret objects | `kubectl apply -f secret.yaml` |
| **Cloud Functions** | Platform environment variables | AWS Lambda, Google Functions, Azure |
| **Managed secrets** | Secrets manager | AWS Secrets Manager, Vault, KeyVault |
| **CI/CD** | Repository secrets | GitHub Actions, GitLab CI, CircleCI |
| **Encryption at rest** | Encrypted file + decryption on startup | GPG, AWS KMS |

---

## Resources

- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [12 Factor App: Store config in environment](https://12factor.net/config)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
