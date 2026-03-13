---
type: distilled-context
module: deployment
project: fitness-app
status: active
updated: 2026-03-11
tags:
  - deployment
  - docker
  - arm64
  - nginx
  - server
---

# Deployment Distilled Context

## Purpose
Deployment covers how the app is built, run, and exposed in the target infrastructure.

## Core Flow
- Services are containerized and run via Docker Compose.
- Backend, database, and reverse proxy must work together reliably.
- The target environment must remain compatible with ARM64 constraints.

## Source of Truth
- Dockerfiles
- docker-compose files
- deployment notes
- nginx/reverse proxy config
- server setup documentation

## Key Contracts
- The stack must remain deployable on ARM64-compatible infrastructure.
- Service-to-service communication must use stable internal networking.
- Public access must be aligned with proxy/domain configuration.

## Known Pitfalls
- Architecture mismatch on ARM64
- Misconfigured container networking
- Wrong hostnames/ports between services
- Missing persistence or environment variables

## Relevant Files
- `Dockerfile`
- `docker-compose.yml`
- `nginx/...`

## Related Notes
- [[10-deployment/docker]]
- [[10-deployment/cloudflare]]
- [[01-project/constraints]]