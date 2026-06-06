# Global Crisis Market Intelligence Platform

Full-stack crisis market dashboard built from the PRD:

- React + Vite frontend with dashboard, event detail, search, chat, and history pages.
- FastAPI backend with news ingestion, AI summarization, sector prediction, search, and chatbot endpoints.
- Supabase-ready schema and REST repository.
- Local demo mode that runs without API keys or a database.

## Project Structure

```text
backend/
  app/
    routes/          FastAPI routers
    services/        news, AI, processing, scheduler services
    repository.py    Supabase REST + in-memory demo repository
  requirements.txt
  supabase.sql
frontend/
  src/
    pages/
    components/
  package.json
```

## Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

The API starts at `http://localhost:8000`.

Useful endpoints:

- `GET /health`
- `GET /api/events`
- `POST /api/events/fetch`
- `GET /api/predictions/summary`
- `GET /api/search?q=oil`
- `POST /api/chat`

## Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

The app starts at `http://localhost:5173`.

## Supabase Setup

1. Create a Supabase project.
2. Run `backend/supabase.sql` in the SQL editor.
3. Put these values in `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

The backend uses the service role key, so deploy it only on the server side.

## News and AI Providers

Demo mode works with no keys. To enable live ingestion, set one news provider key:

```env
NEWS_PROVIDER=gnews
GNEWS_API_KEY=your-key
```

or:

```env
NEWS_PROVIDER=newsapi
NEWS_API_KEY=your-key
```

For AI, choose OpenAI or Anthropic:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini
```

or:

```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
```

## Deployment Notes

- Vercel frontend: set `VITE_API_BASE_URL` to the Render backend URL.
- Render backend: use Python 3.11+, install from `backend/requirements.txt`, and run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- Keep all API keys in deployment environment variables.
- The backend scheduler runs news fetches every 15 minutes by default.
