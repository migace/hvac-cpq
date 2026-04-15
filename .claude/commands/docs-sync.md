Verify that project documentation in `docs/` is in sync with the current codebase. Detect drift, missing entries, and outdated descriptions.

## Documentation files to check

| Doc file | What to verify against |
|---|---|
| `docs/architecture.md` | Actual directory structure, layers, infrastructure setup |
| `docs/erd.md` | Models in `apps/backend/app/db/models.py` |
| `docs/feature-scope.md` | Implemented features in routes, services, and frontend |
| `docs/services.md` | Service classes in `apps/backend/app/services/` |
| `docs/api-conventions.md` | Actual API routes, error handling, status codes |
| `docs/testing.md` | Test files in `apps/backend/tests/`, test infrastructure |
| `docs/demo-families.md` | Seed data in `apps/backend/scripts/seed_demo_data.py` |
| `docs/running.md` | docker-compose.yml, package.json scripts, actual setup steps |
| `CLAUDE.md` | Overall project structure and guidelines |

## Steps

### 1. Read all documentation files

Read every file listed above to understand what's currently documented.

### 2. Read corresponding source code

For each doc file, read the relevant source files to understand the actual state.

### 3. Compare and detect drift

For each doc file, check:

#### `docs/erd.md`
- Are all models from `models.py` listed in the ERD?
- Are all columns/fields documented?
- Are relationships accurate?
- Does the Mermaid diagram match the actual schema?

#### `docs/services.md`
- Are all service classes in `apps/backend/app/services/` documented?
- Are method signatures accurate?
- Are new services missing from the docs?
- Are removed services still listed?

#### `docs/feature-scope.md`
- Are all API endpoints reflected in the feature list?
- Are frontend pages/features covered?
- Are there implemented features not mentioned?
- Are there documented features that don't exist?

#### `docs/api-conventions.md`
- Does the error shape match `apps/backend/app/core/error_response.py`?
- Are all status codes used in routes reflected?
- Is the SSE protocol for the agent endpoint accurate?

#### `docs/architecture.md`
- Does the directory structure match reality?
- Are all layers listed (API, Service, Domain, Repository, DB)?
- Is the infrastructure description (Docker, Turborepo) accurate?

#### `docs/testing.md`
- Are all test files listed?
- Is the test infrastructure description (conftest, testcontainers) accurate?
- Are test categories complete?

#### `docs/demo-families.md`
- Do documented families match `seed_demo_data.py`?
- Are attributes, rules, and pricing rules accurate?

#### `docs/running.md`
- Do setup commands actually work with current config?
- Are ports, env vars, and service names correct?
- Does docker-compose.yml match the documented setup?

#### `CLAUDE.md`
- Is the repository structure accurate?
- Is the documentation index complete (all docs/ files listed)?
- Are development guidelines still relevant?

### 4. Report findings

Structure the report as:

### Documentation Sync Report

#### In sync
List docs that are fully up to date — briefly confirm.

#### Drift detected
For each issue:
- **File**: which doc file
- **Section**: which part is outdated
- **Current docs say**: what the docs claim
- **Code actually has**: what the reality is
- **Severity**: cosmetic (minor wording) | outdated (wrong info) | missing (gap in docs)
- **Suggested fix**: specific text change

#### Missing documentation
Things that exist in code but have no documentation at all.

### 5. Apply fixes

After presenting the report, ask the user if they want to apply the fixes. If yes, update the documentation files directly.

## Important

- Read BOTH the docs and the source code — don't just check one side
- Pay attention to new files/services/routes that were added after docs were written
- Don't flag style differences — focus on factual accuracy
- If a doc file doesn't exist yet, note it as "missing documentation" rather than an error
- Don't rewrite docs from scratch — make targeted updates to fix specific drift
- Preserve the existing writing style and structure of each doc file
