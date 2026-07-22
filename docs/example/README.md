# Worked example

Output of:

```bash
geck launch \
  --project-name "My Project" \
  --goal "Ship a REST API with auth, rate limiting, and OpenAPI docs. The service replaces the legacy PHP endpoint currently used by the mobile app, and must be a drop-in replacement at the same paths." \
  --profile api \
  --criterion "All endpoints have integration tests" \
  --criterion "OpenAPI spec is published and matches the live API" \
  --non-goal "Not building a frontend" \
  --non-goal "Not migrating the database schema in this effort" \
  --harness claude-code \
  --merge-mode approve \
  --work-branch dev \
  --charter "Survey the existing PHP endpoint and auth middleware before designing the new API's route table." \
  --backlog-seed "Add rate limiting middleware" \
  --backlog-seed "Publish OpenAPI docs at /docs"
```

- [`mission-spec.md`](mission-spec.md) — the durable mission document.
- [`launch-prompt.md`](launch-prompt.md) — the prompt you'd paste into Claude Code.

`repo:` in the frontmatter is a placeholder here — a real run auto-detects it
from `git remote get-url origin` when `--path` is itself a git repo root.
