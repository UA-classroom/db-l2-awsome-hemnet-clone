# Repository Guidelines

## Project Structure & Module Organization
- Backend root holds FastAPI app (`app.py`), database helpers (`db.py`), setup scripts (`db_setup.py`, `schema.sql`, `seed_inserts.sql`, `test_queries.sql`) and Pydantic schemas (`schemas.py`).
- Env and connection details live in a local `.env` (vars: `DATABASE`, `PASSWORD`); do not commit it.
- Frontend lives in `frontend/` (Vite + React + Tailwind). App code sits in `frontend/src/`; static assets in `frontend/public/`.

## Build, Test, and Development Commands
- Backend environment: `python -m venv .venv && source .venv/bin/activate` then `pip install -r requirements.txt`.
- Run API locally: `uvicorn app:app --reload` (reload for dev). Use `db_setup.py` as a script to create schema: `python db_setup.py`.
- Frontend install: `cd frontend && npm install` (uses `package-lock.json`).
- Frontend dev server: `npm run dev` (Vite). Production build: `npm run build`. Preview built assets: `npm run preview`. Lint React/TS: `npm run lint`.

## Coding Style & Naming Conventions
- Python: follow PEP 8, 4-space indents, prefer type hints on public functions and request/response models. Keep DB helpers thin (no business logic).
- SQL: keep schema changes in `schema.sql`; seed/test data in dedicated `seed_inserts.sql` or `test_queries.sql`.
- Frontend: TypeScript + React hooks. Keep components in `frontend/src` with PascalCase file/component names; colocate CSS/Tailwind usage per component. Run ESLint before committing.

## Testing Guidelines
- No formal suite yet; prefer `pytest` for backend (name tests `test_*.py`) and React Testing Library/Vitest for frontend. Target critical paths: database queries, API endpoints, and core UI flows. Add sample data via `test_queries.sql` when possible.

## Commit & Pull Request Guidelines
- Use concise, imperative commit messages (e.g., "add listing filter API", "fix lint errors").
- PRs should describe intent, key changes, and testing performed; link related issues. Include screenshots or API examples when UI or contract changes occur. Keep changes scoped and ensure lint/build pass before requesting review.

## Security & Configuration Tips
- Keep secrets in `.env`; never commit credentials. Use least-privilege DB users for local testing. Validate all request payloads via Pydantic schemas to avoid unsafe inputs.
