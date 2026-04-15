Analyze the current git diff and create a commit with a well-crafted message following this repository's conventions.

## Steps

1. Run `git status` to see all changed, staged, and untracked files.
2. Run `git diff` and `git diff --cached` to understand both staged and unstaged changes.
3. Run `git log --oneline -10` to see recent commit message style.
4. Analyze the changes:
   - Determine the nature: new feature (`feat`), bug fix (`fix`), refactor (`refactor`), chore (`chore`), docs (`docs`), test (`test`), style (`style`).
   - Identify which area of the monorepo is affected (backend, frontend, docs, root).
   - Summarize the "why" not just the "what".
5. Stage relevant files — prefer specific file paths over `git add -A`. Never stage files that look like secrets (`.env`, credentials, API keys).
6. Create the commit using this format:

```
type: concise description of what changed and why

Optional body with more details if the change is non-trivial.
Explain motivation, not mechanics.
```

## Commit style rules (derived from this repo)

- Use conventional commit prefixes: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `style`
- Subject line: lowercase, no period, imperative mood, under 72 characters
- If changes span multiple areas, mention the most important one in the subject
- Body is optional — use it only when the subject alone is insufficient

## Important

- Do NOT stage or commit `.env` files, credentials, or secrets
- Do NOT use `git add -A` or `git add .` — stage files explicitly
- If there are no changes to commit, inform the user instead of creating an empty commit
- Show the user what you plan to commit and the proposed message BEFORE committing
- Use a HEREDOC to pass the commit message to git
