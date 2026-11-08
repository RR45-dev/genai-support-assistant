# Local Deployment

1. Copy `.env.example` to `.env` and fill in any LLM credentials (optional).
2. `docker-compose up` — starts Postgres (pgvector), the FastAPI/RAG backend,
   and the Next.js frontend.
3. On boot the backend runs `app.ingest` to load `backend/docs/*.md` into the
   vector store before serving requests.
4. Frontend is available on `:3000`, backend GraphQL on `:8000/graphql`.
