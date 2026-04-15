Perform a thorough code review of the current branch's changes, checking against this project's conventions and best practices defined in CLAUDE.md.

## Steps

1. Identify the base branch (usually `main`) and the current branch.
2. Run `git log main..HEAD --oneline` to understand all commits in this PR.
3. Run `git diff main...HEAD` to see the full diff against the base branch.
4. Read `CLAUDE.md` to refresh project conventions and guidelines.
5. If needed, read relevant `docs/` files for deeper context (architecture, API conventions, testing strategy).
6. Review the changes using the checklist below.

## Review checklist

### Architecture & design (from CLAUDE.md)
- [ ] No hardcoded product parameters in route handlers
- [ ] Domain remains data-driven
- [ ] Pricing is separate from validation
- [ ] Rules are separate from storage
- [ ] Quote snapshots remain immutable
- [ ] Explicit business logic preferred over hidden ORM magic
- [ ] No premature abstractions

### Monorepo conventions
- [ ] Backend changes are in `apps/backend/`
- [ ] Frontend changes are in `apps/frontend/`
- [ ] Documentation changes are in `docs/`
- [ ] No cross-app import violations

### Code quality
- [ ] No security vulnerabilities (SQL injection, XSS, command injection, OWASP top 10)
- [ ] No secrets or credentials committed
- [ ] Error handling is appropriate (not excessive, not missing at boundaries)
- [ ] No dead code or unnecessary comments added
- [ ] No unrelated changes mixed into the PR

### Business rules (if applicable)
- [ ] Referenced attributes exist in the family
- [ ] Rule behavior is deterministic
- [ ] Error messages are business-readable
- [ ] Tests cover valid and invalid configurations

### Pricing rules (if applicable)
- [ ] Exactly one active base price rule per family
- [ ] Fixed and percentage logic clearly separated
- [ ] Structured pricing breakdown returned

### Technical calculations (if applicable)
- [ ] Run only on validated configuration values
- [ ] Unit handling is explicit
- [ ] Deterministic outputs
- [ ] API tests for expected formulas

### Frontend (if applicable)
- [ ] TypeScript types are correct and not using `any` unnecessarily
- [ ] No hardcoded API URLs (should use proxy `/api/*`)
- [ ] Components are reasonably sized and focused

### Backend (if applicable)
- [ ] Layered architecture respected (API -> Service -> Domain -> Repository)
- [ ] SQLAlchemy queries are efficient
- [ ] Alembic migrations are reversible if present
- [ ] Proper use of async where needed

## Output format

Structure the review as:

### Summary
One paragraph describing what this PR does.

### Strengths
What's done well — acknowledge good patterns.

### Issues
Categorized as:
- **Critical** — must fix before merge (bugs, security, data loss risk)
- **Important** — should fix (convention violations, design concerns)
- **Minor** — nice to fix (style, naming, small improvements)

### Suggestions
Optional improvements that go beyond fixing issues.

For each issue, reference the specific file and line, explain what's wrong, and suggest a fix.
