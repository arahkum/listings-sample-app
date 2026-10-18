# Agent rules for listings-sample-app

This is a small FastAPI service for a classifieds-style listings API (create,
search). It's the target app for the agentic-ticket-to-pr pipeline's
spec-driven implementation exercises (Step 6).

## Project structure

- `app/models.py` - Pydantic models (`ListingCreate`, `Listing`, `ListingStatus`).
- `app/storage.py` - in-memory store. No database; keep it that way unless a
  ticket explicitly asks for persistence.
- `app/main.py` - FastAPI routes.
- `tests/test_listings.py` - pytest + FastAPI `TestClient`.

## Rules for implementing a ticket

1. Work on a feature branch named `feature/<short-slug>`, never commit
   directly to `main`.
2. Every new behavior needs a test in `tests/`. Do not reduce existing test
   coverage.
3. Keep changes scoped to the ticket. Don't refactor unrelated code in the
   same PR.
4. Validate all request bodies with Pydantic (`Field` constraints), the same
   pattern already used in `app/models.py`.
5. Run `pytest` before committing; all tests must pass.
6. Don't add a database, auth, or new third-party services unless the ticket
   asks for it.

## Commands

- Install: `pip install -r requirements.txt`
- Run tests: `pytest`
- Run the app: `uvicorn app.main:app --reload`
