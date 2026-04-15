Review all changed code in the working tree for opportunities to simplify, improve reuse, and raise quality — then apply the fixes.

## Steps

1. Run `git diff` to see unstaged changes, and `git diff --cached` for staged changes. If no local changes exist, compare `git diff main...HEAD` for the branch.
2. Read `CLAUDE.md` to refresh the project's design principles.
3. For each changed file, read the full file (not just the diff) to understand context.
4. Analyze the changes against the criteria below.
5. Present findings in a structured report.
6. After presenting findings, apply the fixes directly — do not just suggest, actually make the changes.

## Analysis criteria

### Reuse & duplication
- Is there duplicated logic that could use an existing utility or service?
- Are there patterns already established in the codebase that this code should follow instead of reinventing?
- Could any new code be consolidated with existing similar code?

### Simplification
- Can any complex logic be expressed more simply?
- Are there unnecessary abstractions, wrappers, or indirection layers?
- Can conditionals be simplified or flattened?
- Are there over-engineered solutions for simple problems?
- Can any loops be replaced with more idiomatic constructs?

### Dead code & noise
- Are there unused imports, variables, or functions?
- Are there commented-out code blocks that should be removed?
- Are there unnecessary type assertions or casts?
- Are there redundant error checks that can't actually fail?

### Consistency with project conventions
- Does the code follow the layered architecture (API -> Service -> Domain -> Repository)?
- Is business logic in the right layer?
- Are naming conventions consistent with the rest of the codebase?
- Does the code respect the data-driven design principle?

### Performance (only obvious issues)
- N+1 query patterns
- Unnecessary database round-trips
- Missing indexes for new query patterns
- Unnecessarily loading full objects when only IDs are needed

## Output format

### Summary
One sentence: what was changed and the overall quality assessment.

### Findings
For each finding:
- **File**: path and line range
- **Category**: reuse | simplification | dead code | consistency | performance
- **Severity**: cleanup (nice to have) | improve (should do) | important (must do)
- **Current**: what the code does now
- **Suggested**: what it should do instead
- **Why**: brief justification

### Applied changes
List each change made with before/after snippets.

## Important
- Do NOT add features or expand scope
- Do NOT add comments, docstrings, or type annotations to unchanged code
- Do NOT refactor working code that isn't part of the current changes
- Focus only on the changed code and its immediate context
- If there's nothing to improve, say so — don't invent issues
