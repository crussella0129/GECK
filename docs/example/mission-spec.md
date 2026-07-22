---
geck: '2.0'
project: My Project
created: 2026-07-21
profile: api
harness: claude-code
merge_mode: approve
work_branch: dev
repo: https://github.com/you/my-project.git
sprint_loops_ref: 2026-07-21
---
# Mission: My Project

## Goal

Ship a REST API with auth, rate limiting, and OpenAPI docs. The service replaces the legacy PHP endpoint currently used by the mobile app, and must be a drop-in replacement at the same paths.

## Success Criteria

Mission-level definition of done. Checked off across sprints, not per-sprint.

- [ ] All endpoints have integration tests
- [ ] OpenAPI spec is published and matches the live API

## Non-Goals

Explicit exclusions — the anti-drift fence.

- Not building a frontend
- Not migrating the database schema in this effort

## Constraints

- **Languages:** Python 3.11+, TypeScript/Node.js, Go, Rust

- **Frameworks:** FastAPI, Flask, Django REST Framework, Express, NestJS, Hono, GraphQL, gRPC, tRPC

- **Platforms:** Linux, Docker, Kubernetes

- **Must use:** OpenAPI/Swagger documentation, proper HTTP methods and status codes, request validation, structured logging

- **Must avoid:** SQL injection, exposing stack traces in production, missing authentication on protected routes, N+1 query problems

## Working Agreement

- **Merge mode:** approve — a human approves each sprint's PR before it merges.
- **Work branch:** dev

## Sprint 0 Charter

Survey the existing PHP endpoint and auth middleware before designing the new API's route table.

## Backlog Seeds

- T-101 (backlog): Add rate limiting middleware
- T-102 (backlog): Publish OpenAPI docs at /docs

## Amendment Protocol

This file is amended by humans only. Agents proposing a change record an ADR
in `decisions.md` referencing the relevant section; the spec itself is edited
by the human. Each sprint's Research Phase re-reads this file and reports
drift.
