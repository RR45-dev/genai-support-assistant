# GenAI Support Assistant — RAG over Internal Docs

## Business problem

Retail and IT-services support teams spend a large share of their time answering the same repetitive questions (return windows, shipping cutoffs, warranty terms) that are already written down somewhere in internal docs — customers and even junior agents just can't find them fast enough. This assistant answers those questions by retrieving the relevant doc passage and grounding the response in it, instead of guessing.

## Architecture

```
Next.js/TS chat UI --(GraphQL)--> FastAPI + Strawberry GraphQL --(pgvector similarity search)--> PostgreSQL
                                          |
                                          v
                              Azure OpenAI (generation) — or extractive fallback with no API key
```

1. **ingest.py** chunks Markdown docs (`backend/docs/`, or pulled from an S3 bucket if `DOCS_S3_BUCKET` is set) and embeds each chunk with a local `sentence-transformers` model, storing the vectors in **PostgreSQL** via the **pgvector** extension.
2. **rag.py** embeds the incoming question, retrieves the top-k most similar chunks via a pgvector cosine-distance query, and either (a) sends the question + retrieved context to **Azure OpenAI** for a grounded answer, or (b) falls back to returning the most relevant chunk verbatim when no Azure OpenAI credentials are configured — so the whole thing runs locally with zero API keys.
3. A **GraphQL** API (`strawberry-graphql` mounted on FastAPI) exposes a single `askQuestion(question)` query returning the answer text and the source documents used.
4. The **Next.js + TypeScript** frontend is a minimal chat UI that calls the GraphQL endpoint and displays which docs backed each answer.
5. `infra/main.tf` (**Terraform**) provisions the Azure Postgres Flexible Server and App Service the backend would run on in production; `.github/workflows/ci.yml` (**GitHub Actions**) builds/tests both services and validates the Terraform.

## Tech stack coverage

Python, TypeScript, JavaScript, React, PostgreSQL (pgvector), GraphQL, Next.js, AWS (optional S3 doc source), Splunk (logging), GitHub Actions, Terraform, Azure (deployment target), Docker.

## Running it locally

```bash
docker compose up --build
```

- Chat UI: http://localhost:3000
- GraphQL playground: http://localhost:8000/graphql

The backend automatically ingests the sample docs (return policy, shipping FAQ, warranty) on startup. Ask things like "Can I return an opened laptop?" or "How fast is expedited shipping?" and check the cited sources.

To use real generation instead of the extractive fallback, set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, and `AZURE_OPENAI_DEPLOYMENT` as environment variables for the `backend` service before starting.

## Re-ingesting docs after edits

```bash
docker compose exec backend python -m app.ingest
```

## Taking it further (what to mention in an interview)

- Add a feedback loop: log which retrieved chunks led to a "this didn't help" click, and use that to prioritize doc rewrites.
- Chunk by heading instead of paragraph count for cleaner citations.
- Add a small eval set of question/expected-answer pairs and a script that scores retrieval precision after each doc-set change.
- Swap the local sentence-transformers model for Azure OpenAI's embeddings API for consistency with the generation step.
