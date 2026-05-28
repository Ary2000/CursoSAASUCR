# AI Agent Instructions

## Purpose
This repository contains a small Python microservices system for a SaaS course assignment. The best way to work with it is to treat each service as an independent FastAPI app and use the root `docker-compose.yml` to run the full system.

## Architecture
- `docker-compose.yml` is the canonical integration entrypoint.
- Services are separate directories with their own `Dockerfile` and `requirements.txt`.
- All services use Python 3.14 and FastAPI / Uvicorn.
- RabbitMQ is the asynchronous messaging backbone for `Torneos` and `Eventos`.

## Services
- `CatalogoJuegos/`: FastAPI catalog service exposing REST endpoints on `/games`.
- `IdenttidadUsuarios/`: FastAPI identity/auth service.
- `Eventos/`: FastAPI + Strawberry GraphQL service for events.
- `Torneos/`: FastAPI tournament service.
- `rabbitmq`: managed by the root compose stack, configured in `docker-compose.yml`.

## Run / development guidance
- Use `docker compose up --build` from the repository root to start the full system.
- Each service can also be developed locally from its own folder via its `requirements.txt` and `uvicorn app:app --host 0.0.0.0 --port 8000` command.
- There is no root Python virtual environment or top-level `requirements.txt`; dependencies are managed per service.

## Testing
- Contract tests exist in `CatalogoJuegos/tests/pact/test_fastapi_pact.py` and `Torneos/tests/pact/test_fastapi_pact.py`.
- These tests use `pytest` and `pact-python` to verify provider behavior against stored contract files.
- When changing APIs, validate the relevant contract tests and update pact files as needed.

## Important conventions
- Service containers are exposed by compose with these ports:
  - `catalogojuegos` => `9090:8000`
  - `eventos` => `8000:8000`
  - `identidad` => `8003:8000`
  - `torneos` => `8004:8000`
- `Eventos` depends on `identidad`, `torneos`, and `rabbitmq`; `Torneos` depends on `catalogo-juegos`, `identidad`, and `rabbitmq`.
- `IdenttidadUsuarios` and `Eventos` use environment variables from compose to locate other services.

## Notes for AI agents
- Prefer root-level compose orchestration for integration changes.
- Prefer editing the service directory that owns the API or contract.
- The root README appears to describe a prior task and may be outdated. Use it only as a reference, not as the authoritative source for current service behavior.
- Do not assume a monorepo package layout; each service is self-contained.
