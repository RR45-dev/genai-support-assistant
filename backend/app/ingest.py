"""
Chunks Markdown support docs and stores their embeddings in Postgres
(pgvector). Run as a one-off script: `python -m app.ingest`.
"""
import os
from app import config, db
from app.embeddings import embed
from app.s3_storage import list_local_docs, download_docs_from_s3


def chunk_text(text: str, max_chars: int = 800) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""
    for p in paragraphs:
        if len(current) + len(p) > max_chars and current:
            chunks.append(current)
            current = p
        else:
            current = f"{current}\n\n{p}" if current else p
    if current:
        chunks.append(current)
    return chunks


def ingest_docs(folder: str = "docs"):
    db.init_schema()

    paths = download_docs_from_s3(folder) if config.S3_BUCKET else list_local_docs(folder)
    if not paths:
        print(f"No .md files found in {folder}/ — nothing to ingest.")
        return

    with db.get_connection() as conn:
        conn.execute("DELETE FROM doc_chunks")  # simple full re-index each run
        for path in paths:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            chunks = chunk_text(text)
            vectors = embed(chunks)
            for chunk, vector in zip(chunks, vectors):
                conn.execute(
                    "INSERT INTO doc_chunks (source, content, embedding) VALUES (%s, %s, %s)",
                    (os.path.basename(path), chunk, vector),
                )
            print(f"Ingested {len(chunks)} chunks from {path}")


if __name__ == "__main__":
    ingest_docs()
