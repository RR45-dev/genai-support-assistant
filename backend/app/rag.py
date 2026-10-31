"""
Retrieval-augmented answer generation. Retrieval always uses the local
pgvector index; generation uses Azure OpenAI when credentials are
configured, and otherwise falls back to a purely extractive answer (the
most relevant chunk verbatim) so the service is demoable with no API keys.
"""
from dataclasses import dataclass
from app import config, db
from app.embeddings import embed


@dataclass
class RetrievedChunk:
    content: str
    source: str
    distance: float


@dataclass
class Answer:
    text: str
    sources: list[str]


def retrieve(question: str, top_k: int = None) -> list[RetrievedChunk]:
    top_k = top_k or config.TOP_K
    [query_vector] = embed([question])
    with db.get_connection() as conn:
        rows = conn.execute(
            """
            SELECT content, source, embedding <=> %s AS distance
            FROM doc_chunks
            ORDER BY distance ASC
            LIMIT %s
            """,
            (query_vector, top_k),
        ).fetchall()
    return [RetrievedChunk(content=r[0], source=r[1], distance=r[2]) for r in rows]


def _extractive_answer(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "I couldn't find anything relevant in the knowledge base yet — try re-running the ingest step."
    return chunks[0].content


def _azure_openai_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    from openai import AzureOpenAI

    client = AzureOpenAI(
        api_key=config.AZURE_OPENAI_API_KEY,
        api_version=config.AZURE_OPENAI_API_VERSION,
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
    )
    context = "\n\n---\n\n".join(c.content for c in chunks)
    response = client.chat.completions.create(
        model=config.AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": (
                "You are a support assistant. Answer ONLY using the provided context. "
                "If the answer isn't in the context, say you don't know."
            )},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content


def answer_question(question: str) -> Answer:
    chunks = retrieve(question)
    if config.AZURE_OPENAI_ENDPOINT and config.AZURE_OPENAI_API_KEY:
        text = _azure_openai_answer(question, chunks)
    else:
        text = _extractive_answer(chunks)
    return Answer(text=text, sources=sorted({c.source for c in chunks}))
