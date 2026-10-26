# Scholarship assistant deployment

The chatbot runs on the FastAPI service. Keep the Groq credential on the backend; do not add it to a `VITE_*` frontend variable.

## Local development

From the repository root, create and use a virtual environment so the `uvicorn`
command uses the installed backend dependencies:

```powershell
py -3.12 -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

Set `DATABASE_URL` in `backend/.env` to a local PostgreSQL database or a
database you have explicitly chosen to use. Do not commit `backend/.env`.
Supabase variables are optional for local development; without a working
Supabase client and credentials, uploaded files use the local `backend/uploads`
directory. Local fallback uploads are not persistent on Render, so configure
Supabase for deployed document storage.

For the frontend, run `npm ci` and `npm run dev` from the repository root.
`.env.development` points to `http://localhost:8000`; use `VITE_API_URL` to
override that address if the backend runs on another host or port.

## Render environment

Set these environment variables for the backend service:

- `DATABASE_URL` — Render PostgreSQL connection URL used by both the API and Alembic migrations.
- `SECRET_KEY` — a long, random secret used for authentication and reset-code hashing; replace any development default.
- `GROQ_API_KEY` — API key from Groq.
- `GROQ_MODEL` — optional; defaults to `llama-3.3-70b-versatile`.
- `BACKEND_URL` — optional public API base URL used for locally stored file links; defaults to Render's `RENDER_EXTERNAL_URL` or `http://localhost:8000`.
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET` — configure persistent document storage. The bucket defaults to `documents`.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` — required to deliver password-reset codes.
- `SMTP_TLS` — optional; defaults to `true`.

With the frontend and backend in this repository, configure Render with the repository root as its Root Directory and use:

```sh
# Build command
cd backend && python -m pip install -r requirements.txt

# Pre-deploy command
cd backend && alembic upgrade head

# Start command
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Alembic reads `DATABASE_URL` from the environment. Run the migration as a pre-deploy step so existing databases receive the new columns before the updated API starts.

For a local checkout of this repository on Windows, apply pending migrations from the repository root with:

```powershell
backend\.venv\Scripts\python.exe -m alembic -c backend\alembic.ini upgrade head
```

The latest migration also repairs an existing `profiles` table if it is missing the optional `aadhaar_no` column.

The chatbot stores each conversation and its messages in the database, scoped to the authenticated user. The assistant receives a maximum of 20 recent stored messages plus the current prompt. Message content is limited to 4,000 characters.

## Chat API

All routes require the existing bearer token:

- `POST /chat/conversations` — create a conversation; accepts `{"title":"..."}`.
- `GET /chat/conversations` — list the signed-in user's conversations.
- `GET /chat/conversations/{id}` — read a conversation and its messages.
- `DELETE /chat/conversations/{id}` — delete a conversation and its messages.
- `POST /chat/conversations/{id}/messages/stream` — stream a response as Server-Sent Events; accepts `{"content":"..."}`. Token events contain `{"token":"..."}`, and a final `done` event contains the conversation ID.

The chatbot endpoint returns a clear `503` response if `GROQ_API_KEY` is not configured. Password-reset responses do not disclose whether an email address is registered. Reset codes expire after 15 minutes, are stored as an HMAC digest, and can only be used once.
